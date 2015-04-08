import  os,math,sys,csv,xlwt
import numpy as np
import matplotlib.pyplot as plt

class TimeHistory(object):
    
    def __init__(self,accel=[],dt=0.0,time=[],filename=None,\
                 fformat=None):
        if filename==None:
            self.npoints=len(accel)
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
        values start at the second line.'''
        f=open(filename,'r')
        dt=float(f.next().split()[1])
        v=[]
        for line in f:            
            v.append(float(line))
        self.npoints=len(v)
        self.SetValues(v)
        time=[dt*i for i in range(self.npoints)]
        self.SetTime(time)

    def SetValues(self,accel):
        self.accel=np.array(accel,dtype='float64')
        
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
            self.dt=self.time[-1]/(self.npoints-1)
            
    def GetFilename(self):
        return self.filename
    
    def GetNumOfPoints(self):
        return self.npoints
    
    def GetTimeStep(self):
        return self.dt

    def GetValues(self):
        return self.accel

    def Plot(self,filename='',ylabel='',show=0, axis=''):
        
        plt.plot(self.time,self.accel)
        plt.xlabel("Time (s)")
        if not ylabel:
            ylabel="Acceleration"
        plt.ylabel(ylabel)

        if axis:
           plt.axis(axis) 

        if show:
            plt.show()
        elif not filename:
            pass
        else:
            plt.savefig(filename, bbox_inches='tight')

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
        
    def __del__(self):pass
        
    
class ResponseSpectra(object):
    def __init__(self,frequency=[],spectra=[],damping=0.0,\
                 name=''):
        self.npoints=0
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
        self.frequency=np.array(frq,dtype='float64')
        self.npoints=len(frq)
        if not self.period:
            #test succeed if frequency is not set yet
            v1=[1.0/x if x < 100.0 else 0.01  for x in v1]
            self.SetPeriod(v1)

    def SetPeriod(self,period):
        self.period=np.array(period,dtype='float64')
        self.npoints=len(period)
        if not self.frequency:
            #test succeed if frequency is not set yet
            v1=[1.0/x if x != 0 else 100.0  for x in v1]
            self.SetFrequency(v1)

    def GetFrequency(self):
        return self.frequency

    def GetPeak(self):
        if self.IsSet():
            return np.amax(self.spectra)
        else:
            return 0
        
    def GetZPA(self):
        """Return the ZPA of the spectrum."""
        if self.IsSet():
            # We assume that the ZPA is the first value of the spectra
            # vector. THIS MUST BE TAKEN WITH CAUTION!!
            return self.spectra[0]
        else:
            return 0
        
    def WriteSpectraCsv(self,*args,**kwargs):
        self.WriteCsv(*args,**kwargs)

    def WriteCsv(self,dir=os.getcwd(),filename=''):
        if not filename:
            filename=self.name+'Damp_'+str(self.damping)+'.csv'
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

        # Open a read the file
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
            v1, v2 = (list(t) for t in zip(*sorted(zip(v1, v22),reverse=True)))
            
            # The last period in the list cannot be zero, which is an
            # infinite frequency. Hence I put it to 0.01 which is
            # ~100Hz and equivalent to the ZPA.
            if v1[-1]==0.0:
                v1[-1]=0.01            
            self.SetPeriod(v1)
        elif type=='frequency':
            # We also impose a sort, just in case the values were not
            # sorted in the csv file, but this time ascending.
            v1, v2 = (list(t) for t in zip(*sorted(zip(v1, v22))))        
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

    def __iter__(self):
        for spectra in self.family:
            yield spectra
        
    def __getitem__(self,index):
        return self.family[index]
                                    
    def __del__(self):pass
        
def Main():
    th=TimeHistory(filename='000042xa_acc.acc',fformat='acc')
if __name__=="__main__":
    Main()
