import  os,math,sys,csv,xlwt
import numpy as np
import matplotlib.pyplot as plt

class TimeHistory(object):
    ## MAK : 26/08/2015. Added self.name variable
    ## MAK : Added export function WriteCsv and WriteXls
    def __init__(self,accel=[],dt=0.0,time=[],filename=None,\
                 fformat=None,name=''):
        if filename==None:
            self.SetValues(accel)
            self.SetTime(time,dt)
        else:
            try:
                self.SetFromFile(filename,fformat)
            except IOError:pass
                # IOError arise when the file does not exists. This
                # can happen for instance when performing a THGE
                # analysis. The object is instantiated with an empty
                # file which is created later on. The call to
                # SetFromFile should be made after the file creation.
        self.name=name
                
    def SetName(self,name):
        self.name=name
    
    def GetName(self):
        return self.name
                
                
    def SetFromFile(self,filename,fformat):
        options = {None:self.UndefinedFormat,
                   'csv':self.ReadFromCsv,
                   'acc':self.ReadFromAcc
                    }
        options[fformat](filename)

    def UndefinedFormat(self,filename):
        raise IOError('Format of file must be specified')
                 
    def ReadFromCsv(self,filename,skip=1):    
        '''Read accelerogram from csv file. assumed format is the
        time values in the first column, the acceleration in the
        second column. By default, it is assumed that the values
        start at the second line.'''
        f=open(filename,'r')
        for i in range(skip):
            _unused=f.next()
        v1=[]
        v2=[]
        for line in f:
            v=[float(x) for x in line.split(',')]
            v1.append(v[0])
            v2.append(v[1])
        self.npoints=len(v2)
        self.SetTime(v1)
        self.SetValues(v2)

    def ReadFromAcc(self,filename):        
        '''Read accelerogram from acc file. The timestep is given on
        the first line. The acceleration is in the first column. The
        values start at the thirdd line.'''
        f=open(filename,'r')
        # First line is useless.
        _unused=f.next()
        # Second line contains number of points and timestep
        line=f.next()
        dt=float(line.split()[1])
        v=[]
        for line in f:            
            v.append(float(line))
        self.npoints=len(v)
        self.SetValues(v)
        self.SetTime(dt=dt)

    def SetValues(self,accel):
        self.accel=np.array(accel,dtype='float64')
        self.npoints=len(accel)
        
    def SetTime(self,time=[],dt=0.0):
        if time==[] and dt<1E-10:
            # All variables are unspecified for now
            return
        elif time==[]:
            self.dt=dt
            time=[i*dt for i in range(self.npoints)]
            self.time=np.array(time,dtype='float64')
        else:
            if self.npoints!=len(time):
                raise SyntaxError('time and frequency vectors must have the same length')
            self.time=np.array(time,dtype='float64')
            self.dt=self.time[1]-self.time[0]
            
    def GetFilename(self):
        return self.filename
    
    def GetNumOfPoints(self):
        return self.npoints
    
    def GetTimeStep(self):
        return self.dt

    def GetValues(self):
        return self.accel

    def Plot(self,dir=os.getcwd(),filename='',ylabel='',show=0, axis=''):
        if not filename:
            filename=self.name+'.png'
        outfile=os.path.join(dir,filename)
        plt.plot(self.time,self.accel)
        plt.xlabel("Time (s)")
        if not ylabel:
            ylabel="Acceleration"
        plt.ylabel(ylabel)

        if axis:
           plt.axis(axis) 

        if show:
            plt.show()
        else:
            plt.savefig(outfile, bbox_inches='tight')

    def GetSpectra(self):pass
        # '''Return the response spectra corresponding to the th.
        # Need an interface with GASPEC.'''        

    def AdjustLength(self,length,check=True):
        if length < self.npoints:
            print 'Warning : The serie is being truncated'
        self.accel.resize(length,refcheck=check)
        self.npoints=length
        self.SetTime(dt=self.dt)

    def AccelInGUnits(self,g=9.81):
        self.accel=self.accel/g

    def WriteTh(self,dir=os.getcwd(),filename='',fformat='csv',*args,**kwargs):
        ## NOT TESTED!!!
        if not filename:
            filename=self.name
        options = {None:self.WriteThCsv,
                   'csv':self.WriteThCsv,
                   'xls':self.WriteThXls
                    }
        options[fformat](dir,filename,*args,**kwargs)

    def WriteThCsv(self,dir=os.getcwd,filename=None):
        ## NOT TESTED!!!
        if filename!=None:
            fname,ext=os.path.splitext(filename)
            if ext != '.csv':
                filename=fname+'.csv'
        else:
            if self.name:
                filename=self.name+'.csv'
            else:
                filename='timehistory.csv'
        path=os.path.join(dir,filename)
        f=open(path,'wb')
        writer=csv.writer(f,dialect='excel')
        for i,val in enumerate(self.time):
             writer.writerow([self.time[i],self.accel[i]])
        f.close()

    def WriteThXls(self,dir,filename):
        ## NOT TESTED!!!
        fname,ext=os.path.splitext(filename)
        if ext not in ['.xls','.xlsx']:
            filename=fname+'.xls'
        path=os.path.join(dir,filename)
        wb = xlwt.Workbook()
        ws=wb.add_sheet('Sheet1')
        ws.write(0,0,'Time')
        ws.write(0,1,'Acceleration')
        for i,val in enumerate(self.time):
             ws.write(i+1,0,val)
             ws.write(i+1,1,self.accel[i])
        wb.save(path)       
        
    def __del__(self):pass

class TimeHistoryFamily(object):
    ## MAK : 26/08/2015. class created 
    def __init__(self,family=[],name=''):
        self.numofth=0
        self.namelist=[]
        self.family=[]
        self.name=name
        if family:
             for th in family:
                 self.AddTimeHistory(th)

    def WriteThFamily(self,fformat='csv',*args,**kwargs):
        ## NOT TESTED!!!
        options = {None:self.WriteThFamilyCsv,
                   'csv':self.WriteThFamilyCsv,
                   'xls':self.WriteThFamilyXls
                    }
        options[fformat](*args,**kwargs)


    def WriteThFamilyCsv(self,*args,**kwargs):
        for th in self.family:
            th.WriteTh(fformat=csv,*args,**kwargs)
                
    def WriteThFamilyXls(self,dir=os.getcwd(),filename=''):
        if not self.name:
            filename='Accelerograms.xls'
        else:
            filename=self.name+'.xls'
        path=os.path.join(dir,filename)        
        wb = xlwt.Workbook()
        for th in self.family:
            sheetname=th.GetName()
            ws=wb.add_sheet(sheetname)
            ws.write(0,0,'Time')
            ws.write(0,1,'Acceleration')
            for i,val in enumerate(th.accel):
                ws.write(i+1,0,th.time[i])
                ws.write(i+1,1,th.accel[i])
        wb.save(path)
        
    def Plot(self,dir=os.getcwd(),show=0,**kwargs):
        '''Plot the th in the family in separate graphs'''
        for th in self.family:
            th.Plot(dir,show=show,**kwargs)
                        
    def AddTimeHistory(self,newth):
        self.family.append(newth)
        self.numofth+=1
        self.namelist.append(newth.name)

    # def PlotFamily(self,filename='',ylabel='',show=0,axis=''):
        # sf=self.GetSubFamilyDamping(damping)
        # sf.Plot(filename,ylabel,show,axis)

    def __iter__(self):
        for th in self.family:
            yield th
        
    def __getitem__(self,index):
        return self.family[index]
                                    
    def __del__(self):pass
                
    
class ResponseSpectra(object):
    def __init__(self,frequency=[],spectra=[],damping=0.05,\
                 name=''):
        if len(frequency)!=len(spectra):
            raise SyntaxError('Frequency and spectra should have the\
                              same length')
                              
        self.npoints=len(frequency)
        self.damping=damping
        self.SetSpectra(spectra)
        self.SetFrequency(frequency)
        self.name=name

    def __str__(self):        
        return "Frequency :"+str(self.frequency)+"\nSpectra :"+str(self.spectra)
        
    def SetDamping(self,damping):
        self.damping=damping

    def GetDamping(self):
        return self.damping

    def SetName(self,name):
        self.name=name
    
    def GetName(self):
        return self.name

    def IsSet(self):
        '''return true if the spectra is already set, 0 othherwise'''
        return (self.npoints>0)
        
    def SetSpectra(self,accel):
        # We assume the accel values are passed as a list and we
        # convert it to an array.
        self.spectra=np.array(accel,dtype='float64')

    def SetFrequency(self,frq):
        # Set the frequency at which the spectra is defined. The
        # argument frq is a list of values already sorted in ascending
        # order.
        # MAK (08/04/2015): The function also sets the period now.
        self.frequency=np.array(frq,dtype='float64')
        self.npoints=len(frq)
        # Set the period from the frequency
        v1=[1.0/x if x < 100.0 else 0.0  for x in self.frequency]
        self.period=np.array(v1,dtype='float64')

    def SetPeriod(self,period):
        # function called if the response spectra is initialized by
        # (period,acceleration) couples in a text file for instance.
        # The argument period is a list, already sorted in descending
        # order.
        # MAK (08/04/2014): The function also sets the acceleration.
        self.period=np.array(period,dtype='float64')
        self.npoints=len(period)
        #set the frequency
        v1=[1.0/x if x != 0 else 100.0  for x in self.period]
        self.frequency=np.array(v1,dtype='float64')
        
    def GetFrequency(self):
        return self.frequency

    def GetPeak(self):
        if self.IsSet():
            return np.amax(self.spectra)
        else:
            return 0
        
    def GetZPA(self):
        """Return the ZPA of the spectrum."""
        # MAK (09/04/2015): The convention has changed and the ZPA is
        # the last value in teh acceleration spectra.
        if self.IsSet():
            # We assume that the ZPA is the last value of the spectra
            # vector. THIS MUST BE TAKEN WITH CAUTION!!
            return self.spectra[-1]
        else:
            return 0
        
    def WriteSpectraCsv(self,*args,**kwargs):
        self.WriteCsv(*args,**kwargs)

    def WriteCsv(self,dir=os.getcwd(),filename=''):
        if not filename:
            filename=self.name+'_Damp_'+str(self.damping)+'.csv'
        path=os.path.join(dir,filename)
        f=open(path,'wb')
        writer=csv.writer(f,dialect='excel')
        for i,val in enumerate(self.frequency):
            writer.writerow([self.frequency[i],self.spectra[i]])
        f.close()

    def WriteSpectraXls(self,dir=os.getcwd(),filename=''):
        if not filename:    
            filename=self.name+'Spectra.xls'
        sheetname='Damp='+str(self.damping)
        path=os.path.join(dir,filename)
        wb = xlwt.Workbook()
        ws=wb.add_sheet(sheetname)
        ws.write(0,0,'Frequency')
        ws.write(0,1,'Acceleration')
        for i,val in enumerate(self.frequency):
            ws.write(i+1,0,val)
            ws.write(i+1,1,self.spectra[i])
        wb.save(path)
        

    def Plot(self,filename='',ylabel='',show=0,axis=''):
        legend=self.name+" - D="+str(self.damping)
        plt.loglog(self.frequency,self.spectra,label=legend)
        #location : lower right corner
        plt.legend(loc=0)
        plt.xlabel("Frequency")
        if axis:
           plt.axis(axis)     
        if not ylabel:
            ylabel="Acceleration"
        plt.ylabel(ylabel)
        #Add grid on the graph
        plt.grid(b=True, which='both',color='0.65',linestyle='-')
        if show:
            plt.show()
        elif not filename:
            pass
        else:
            plt.savefig(filename, bbox_inches='tight')

    def ReadFromCsv(self,filename,type='period',skip=1):        
        '''
        Initialize from a csv file. We assume by default that the
        format of the file is period in the first column and
        acceleration in the second. An alternative is to specify the
        frequency in the first column and acceleration in the second,
        by setting type to "frequency"'''
        # MAK(08/04/2015): changed to allow definition
        # from (period,acc) couples or from (frq,acc) couples.  Open a
        # read the file. The convention is that the acceleration
        # values are sorted in increasing order of frequencies. Hence,
        # the list of frequencies is in ascending order, while the
        # list of period is in descending order.        
        f=open(filename,'r')
        for i in range(skip):
            _unused=f.next()            
        v1=[]
        v2=[]
        for line in f:
            v=[float(x) for x in line.split(',')]
            v1.append(v[0])
            v2.append(v[1])
        f.close()

        # The input can be period|accel or frequency|accel. The
        # treatment is different:
        if type=='period':
            # First, we order the two columns so that the acceleration
            # vector correspond to increasing frequencies. The
            # following lines sort the two lists according to
            # v1, in descending order.
            v1, v2 = (list(t) for t in zip(*sorted(zip(v1, v2),reverse=True)))
            
            # The last period in the list cannot be zero, which is an
            # infinite frequency. Hence I put it to 0.01 which is
            # ~100Hz and equivalent to the ZPA.
            if v1[-1]==0.0:
                v1[-1]=0.01            
            self.SetPeriod(v1)
        elif type=='frequency':
            # We also impose a sort, just in case the values were not
            # sorted in the csv file, but this time ascending.
            v1, v2 = (list(t) for t in zip(*sorted(zip(v1, v2))))        
            self.SetFrequency(v1)
        else:
            raise SyntaxError("format of spectrum is badly specified.\
                              Use either type='period', or type='frequency'")
                        
        # assume the spectra is given for a damping of 0.05, it
        # doesn't matter
        self.SetSpectra(v2)
        
    def CopySpectra(self,spec):
        self.spectra=spec.spectra
        self.frequency=spec.frequency
        self.damping=spec.damping
        self.npoints=spec.npoints
        
    # THIS DOESN'T WORK. SEE THE Broaden FUNCTION BELOW.
    def Broaden0(self):
        '''Broadening of spectra according to R.G.1.122'''
        specel=[0]*self.npoints
        option = {1:self.is_increasing,
                  2:self.is_decreasing,
                  3:self.is_peak,
                  4:self.is_valley}
            
        # Compute initial sign of gradient
        grad_0=np.sign(self.spectra[1]-self.spectra[0])
        for j,freq in enumerate(self.frequency):
            print j,freq
            try:
                grad=np.sign(self.spectra[j+1]-self.spectra[j])
            except IndexError:
                grad=grad_0
            print grad
            if grad_0==grad:
                if grad>=0:
                    print 'increasing'
                    specel=option[1](specel,j)
                else:
                    print 'decreasing'
                    specel=option[2](specel,j)
            else:
                if grad<0:
                    print 'peak'
                    specel=option[3](specel,j)
                else:
                    print 'valley'
                    specel=option[4](specel,j)
            grad_0=grad
                    
        self.SetSpectra(specel)
                    
    def is_increasing(self,spec,j):
        if j==(len(spec)-1):
            spec[j]=self.spectra[j]
        elif spec[j]==0:
            k=0
            fac=1./1.15
            try:
                while (self.frequency[j]>self.frequency[j+k+1]*fac):
                    k=k+1
            except IndexError:
                k=k-1
            print 'k=',k
            fj=self.frequency[j]
            fm=self.frequency[j+k]
            fk=self.frequency[j+k+1]
            sm=self.spectra[j+k]
            sk=self.spectra[j+k+1]
            spec[j]=sm+(sk-sm)*(fj-fm*fac)/(fk*fac-fm*fac)
        print 'spec[j]=',spec[j] 
        return spec 

    def is_decreasing(self,spec,j):
        if j==0 or j==(len(spec)-1):
            spec[j]=self.spectra[j]
        # Added this test for the case where we passed a peak, the
        # values are then set to the values of the peak and nothing
        # has to be done. Thus we only compute a new values if the
        # broadened spectra is still equal to 0. It is a bit ugly but
        # didn't know how else to do this...
        elif spec[j]==0:
            k=0
            fac=1.15
            try:
                while (self.frequency[j]>self.frequency[j+k+1]*fac):
                    k=k+1
            except IndexError:
                k=k-1

            fj=self.frequency[j]
            fi=self.frequency[j-1]
            fac=1.15
            sj=self.spectra[j]
            si=self.spectra[j-1]
            spec[j]=sj+(sj-si)*(fj-fj*fac)/(fj*fac-fi*fac)
        print 'spec[j]=',spec[j] 
        return spec

    def is_peak(self,spec,j):
        fj=self.frequency[j]
        fac=1.15        
        for i,freq in enumerate(self.frequency):
            if freq>fj/fac and freq<fj*fac:
                spec[i]=self.spectra[j]
        print 'spec[j]=',spec[j]             
        return spec

    def is_valley(self,spec,j):
        fj=self.frequency[j]
        fk=self.frequency[j+1]
        fac=1/1.15
        sj=self.spectra[j]
        sk=self.spectra[j+1]
        spec[j]=sj+(sk-sj)*(fj-fj*fac)/(fk*fac-fj*fac)
        print 'spec[j]=',spec[j] 
        return spec
    
    def Broaden(self):
        '''Broadening of spectra according to R.G.1.122'''
        ## THIS IS DISGUSTING. JUST AN ADAPTATION FROM GASPEC. No time
        ## to do better for now...
        fp1=1.15
        fm1=1/fp1
        specel=[0]*self.npoints
        am=self.spectra[0]
        ak=self.spectra[1]
        k=1
        if(ak >= am):
            fac=fm1
            grad=1.
            i=0
        else:
            fac=fp1
            grad=-1
            specel[0]=am
            i=1
        ym=fac*self.frequency[0]
        yk=fac*self.frequency[1]
        while i<(len(self.frequency)-1):
            # print len(self.frequency)
            # print 'i=',i,'k=',k
            xi=self.frequency[i]
            if xi>yk:
                ## Not sure this is correct. Had to add this to avoid
                ## errors...
                try:
                    ro=grad*(self.spectra[k+1]-ak)
                except IndexError:
                    ro=grad*(self.spectra[k]-ak)
                if ro>=0:
                    ym=yk
                    am=ak
                    k=k+1
                    ## Here again, there are index problems. this
                    ## should be cleaner
                    try:
                        yk=fac*self.frequency[k]
                        ak=self.spectra[k]                
                    except IndexError:                        
                        yk=self.frequency[self.npoints-1]
                        ak=self.spectra[self.npoints-1]
                else:
                    grad=-grad
                    if grad>0:
                        #valley
                        fac=fm1
                        yk=fac*self.frequency[k]
                        for j in range(1,k+1):
                            i=k-j
                            if self.frequency[i]<=yk:
                                i=i+1
                                ym=yk
                                am=ak
                                k=k+1
                                try:
                                    yk=fac*self.frequency[k]
                                except IndexError:
                                    yk=self.frequency[self.npoints-1]
                                ak=self.spectra[k] 
                                break
                    else:
                        #peak
                        fac=fp1
                        for j in range(i,k+1):
                            if specel[j]<ak:
                                specel[j]=ak
                        i=k+1
                        ym=self.frequency[k]
                        yk=fac*ym
                        am=ak                      
            else:
                ei=am+(ak-am)*(xi-ym)/(yk-ym)
                if ei>specel[i]:
                    specel[i]=ei
                i=i+1
        specel[self.npoints-1]=self.spectra[self.npoints-1]
        self.SetSpectra(specel)
                                        

            
    def __del__(self):pass

class SpectraFamily(object):
    def __init__(self,family=[]):
        self.envelope=ResponseSpectra(name='Envelope')
        self.average=ResponseSpectra(name='Average')
        self.numofspec=0
        self.namelist=[]
        self.family=[]
        if family:
            for rs in family:
                self.AddSpectra(rs)
                
    def WriteSpectraXls(self,dir=os.getcwd(),filename=''):
        if not filename:    
            filename='ResponseSpectra.xls'
        path=os.path.join(dir,filename)        
        wb = xlwt.Workbook()
        for spectra in self.family:
            sheetname=spectra.GetName()+'_Damp_'+\
              str(spectra.GetDamping())
            ws=wb.add_sheet(sheetname)
            ws.write(0,0,'Frequency')
            ws.write(0,1,'Acceleration')
            for i,val in enumerate(spectra.frequency):
                ws.write(i+1,0,spectra.frequency[i])
                ws.write(i+1,1,spectra.spectra[i])
        wb.save(path)
        
    def Plot(self,dir=os.getcwd(),filename='PlotSpecFamily.png',show=0,**kwargs):
        '''Plot all the spectra included in the family on one single graph'''
        outfile=os.path.join(dir,filename)
        for spectra in self.family:
            spectra.Plot(**kwargs)
        if show:
            plt.show()
        else:   
            plt.savefig(outfile,bbox_inches='tight')

                    
    def Envelope(self):            
        '''Compute the enveloppe of the spectra family. For the moment it considers
        that all spectra from the list have the same frequency range
        '''
        # Initialize the envelope to the first element of the family
        self.envelope.CopySpectra(self.family[0])
        for spectra in self.family[1:]:
            # Test equality between array
            # spectra.frequency!=self.envelope.frequency:
            if not np.allclose(spectra.frequency,self.envelope.frequency):
                raise NotImplementedError('Frequency range must be strictly identical for every spectrum')
                return
            for idx,acc in enumerate(spectra.spectra):
                self.envelope.spectra[idx]=\
                                max(acc,self.envelope.spectra[idx])            
                    
    def GetEnvelope(self):
        self.Envelope()
        return self.envelope
    
    def Average(self):
        '''For the moment, it considers that all spectra from the
        list have the same frequency range
        '''
        self.average.CopySpectra(self.family[0])
        for spectra in self.family[1:]:
            # Test equality between array
            if not np.allclose(spectra.frequency,self.average.frequency):
                raise NotImplementedError('Frequency range must be strictly identical for every spectrum')
                return
            for idx,acc in enumerate(spectra.spectra):
                self.average.spectra[idx]=self.average.spectra[idx]+acc 
        self.average.spectra=self.average.spectra/self.numofspec
        
    def GetAverage(self):
        self.Average()
        return self.average
        
    def AddSpectra(self,newspec):
        # if newspec.name in self.namelist:
        #     raise TypeError('Error : Name of the spectra already present in the family')
        #print newspec.damping
        self.family.append(newspec)
        self.numofspec+=1
        self.namelist.append(newspec.name)

    def WriteAverageCsv(self):
        if not self.average.IsSet():
            self.Average()
        self.average.WriteSpectraCsv(filename='EnvelopeSpectra.csv')

    def WriteAverageXls(self):
        if not self.average.IsSet():
            self.Average()
        self.average.WriteSpectraXls(filename='EnvelopeSpectra.xls')
        
    def WriteEnvelopeCsv(self):
        if not self.envelope.IsSet():
            self.Envelope()
        self.envelope.WriteSpectraCsv(filename='EnvelopeSpectra.csv')

    def WriteEnvelopeXls(self):
        if not self.envelope.IsSet():
            self.Envelope()
        self.envelope.WriteSpectraXls(filename='EnvelopeSpectra.xls')

    def GetSubFamilyDamping(self,damping):
        speclist=[rs for rs in self.family if rs.damping==damping]
        subfamily=SpectraFamily(speclist)
        return subfamily

    def PlotPerDamping(self,damping,filename='',ylabel='',show=0,axis=''):
        sf=self.GetSubFamilyDamping(damping)
        sf.Plot(filename,ylabel,show,axis)

    def Broaden(self):
        for spectra in self.family:
            spectra.Broaden()
            
    def __iter__(self):
        for spectra in self.family:
            yield spectra
        
    def __getitem__(self,index):
        return self.family[index]
                                    
    def __del__(self):pass
        
def Main():
    th=TimeHistory(filename='000042xa_acc.acc',fformat='acc')

def Test_Elarg1():
    S1=ResponseSpectra(frequency=[
        00.2000,00.3000,00.4000,00.5000,00.6000,00.7000,00.8000,\
        00.9000,01.0000,01.1000,01.2000,01.3000,01.4000,01.5000,\
        01.7000,01.8000,01.8500,01.9000,02.0000,\
        02.1000,02.2000,02.3000,02.4000,02.5000,02.6000,02.7000,\
        02.8000,02.9000,03.0000,03.1500,03.3000,03.4500,03.5000,\
        03.6000,03.8000,04.0000,04.2000,04.4000,04.6000,04.8000,\
        05.0000,05.2500,05.3000,05.5000,05.7500,06.0000,06.2500,\
        06.3000,06.5000,06.7500,07.0000,07.2500,07.4000,07.5000,\
        07.7500,07.9000,08.0000,08.5000,09.0000,09.5000,10.0000,\
        10.5000,11.0000,11.5000,12.0000,12.5000,13.0000,13.5000,\
        14.0000,14.5000,15.0000,16.0000,17.0000,18.0000,20.0000,\
        22.0000,25.0000,28.0000,31.0000,34.0000,38.0000,42.0000,\
        46.0000,50.0000],spectra=[
        5.9041E-02,1.2484E-01,1.5479E-01,2.0932E-01,2.8246E-01,\
        3.6510E-01,4.1445E-01,5.2034E-01,5.9472E-01,7.1328E-01,\
        7.8191E-01,1.0298E+00,1.2317E+00,1.2566E+00,\
        1.2940E+00,1.6526E+00,1.8877E+00,1.6674E+00,\
        1.6638E+00,1.8439E+00,2.1628E+00,1.8578E+00,1.8118E+00,\
        1.7850E+00,1.8978E+00,1.3877E+00,1.5485E+00,1.3071E+00,\
        1.2767E+00,9.8110E-01,1.0161E+00,8.3859E-01,8.7550E-01,\
        6.9499E-01,6.7516E-01,6.1832E-01,5.8253E-01,5.2891E-01,\
        4.8721E-01,4.2382E-01,3.9530E-01,4.2925E-01,4.0510E-01,\
        3.5463E-01,3.5300E-01,3.3540E-01,3.2400E-01,3.3740E-01,\
        3.5991E-01,3.5687E-01,3.4079E-01,3.5719E-01,3.4166E-01,\
        3.4368E-01,3.6472E-01,3.5868E-01,3.5110E-01,3.2518E-01,\
        3.2144E-01,3.2067E-01,3.0912E-01,2.9732E-01,2.8860E-01,\
        2.6941E-01,2.6017E-01,2.5841E-01,2.5071E-01,2.4242E-01,\
        2.3724E-01,2.4242E-01,2.3199E-01,2.3894E-01,2.3233E-01,\
        2.3414E-01,2.3824E-01,2.3597E-01,2.2823E-01,2.2925E-01,\
        2.2715E-01,2.2457E-01,2.2168E-01,2.2155E-01,2.2222E-01,\
        2.2270E-01],name='test')
    S1.Broaden()
    S1.WriteSpectraCsv()

if __name__=="__main__":
    Test_Elarg1()


