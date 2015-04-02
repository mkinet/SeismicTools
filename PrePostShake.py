import re
from subprocess import call
from SeismicTools import *

class Analysis():
    def __init__(self,filename,name=None):        
        #Get working directory : Working directory is set to be the
        #directory where the infile is/will be
        self.pwd=os.path.dirname(filename)
        # Initialize DataFile object
        self.datafiles=DataFile(filename)
        # Name of the analysis. By default, the name of the input file
        # without the extension
        if name==None:
            name=os.path.splitext(filename)
        self.name=name        
        # Initialize results. We mainly focus on the set of spectra
        # generated and on the transfer function.
        self.spectralist=SpectraFamilyShake()
        self.tf=[]
        # Initialize parser
        self.parser=FileParser(self.datafiles)
        
    def GenInfile(self,accfile,template='ShakeTemplate.in'):
        # ShakeTemplate file must in the directory where python is
        # running
        temp=open(template,'r')
        infile=open(self.datafiles.infile,'w')
        for line in temp:
            match=re.search('%%%',line)
            if not match:            
                infile.write(line)
            else:
                infile.write(accfile+'\n')
        temp.close()
        infile.close()
        
    def RunAnalysis(self):
        # DVLPT : Test if input file is empty and create it if needed.
        paramfile=os.path.join(self.pwd,'files.txt')
        self.GenParamFile(paramfile)
        outfile=os.path.join(self.pwd,'shake.out')
        out=open(outfile,'w')
        errfile=os.path.join(self.pwd,'shake.err')
        err=open(errfile,'w')
        call(['shake',paramfile],stdout=out,stderr=err)
        #os.remove(paramfile)
        out.close()
        err.close()
        # Remove error file if empty
        if os.stat(errfile)[6]==0:
            os.remove(errfile)
            
    def GenParamFile(self,fname):
        f=open(fname,'w')
        f.write(self.datafiles.infile+'\n')
        f.write(self.datafiles.outfile1+'\n')
        f.write(self.datafiles.outfile2+'\n')                
        f.close()
        
    def PostAnalysis(self):
        self.parser.ReadResultFiles()
                
    def PostSpectra(self):
        if not self.parser.IsParsed():
            self.PostAnalysis()            
        # Get Spectra from file
        self.parser.GetSpectra(self.spectralist)


    # NEED TO BE TESTED!!!
    def WriteSpectraCsv(self,dir=os.getcwd()):
        # Uses the default filename for now...
        # write results in csv files
        for spectra in self.spectralist:
            spectra.WriteSpectraCsv(dir)

    # NEED TO BE TESTED!!!
    def WriteSpectraXls(self,filename=None,speclist=None):
        if filename is None:
            filename=self.name+'.xls'

        if speclist is None:
            speclist=self.spectralist

        speclist.WriteSpectraXls(self.pwd,filename)
        
    def WriteSpectraXlsDamping(self,damping,filename=None):
        if filename is None:
            filename=self.name+'.xls'
        speclist=self.spectralist.GetSubFamilyDamping(damping)
        self.WriteSpectraXls(filename,speclist)

    def WriteSpectraXlsLayer(self,layer,filename=None):
        if filename is None:
            filename=self.name+'.xls'
        speclist=self.spectralist.GetSubFamilyLayer(layer)
        self.WriteSpectraXls(filename,speclist)

    def PlotSpectra(self,filename=None,ylabel='',show=0,axis=''):
        if filename is None:
            filename=self.name+'.png'
        self.spectralist.Plot(self.pwd,filename,ylabel,show,axis)

    def PlotSpectraDamping(self,damping,filename=None,\
                           ylabel='',show=0, axis=''):
                           
        if filename is None:
            filename=self.name+'.png'

        self.spectralist.PlotPerDamping(damping,filename,ylabel,show,axis)

    def PlotSpectraLayer(self,layer,filename=None,\
                         ylabel='',show=0,axis=''):
        if filename is None:
            filename=self.name+'.png'
        self.spectralist.PlotPerLayer(layer,filename,ylabel,show,axis)

    def GetSpectraDampingLayer(self,damping,layer):
        return self.spectralist.GetSpectraDampingLayer(damping,layer)

    def PostTransferFunction(self):
        if not self.parser.IsParsed():
            self.PostAnalysis()            
        self.parser.GetTF(self.tf)
        self.PlotTf()

    def OutputTransferFunction(self,mode):
        # IMPROVE : Calling this method directly fails if the
        # PostAnalysis and Getspectra methods have not been called
        # beforehand
        #Use a dictionary to define the output mode...
        outputmode={'xls':self.WriteTFXls,
                    'csv':self.WriteTFCsv}
        #Then call the appropriate function
        outputmode[mode]()

    def WriteTFCsv(self):
        for t in self.tf:
            t.WriteCsv(self.pwd)
        
    def WriteTFXls(self):
        for t in self.tf:
            t.WriteXls(self.pwd)

    def PlotTf(self):
        # Plot the various spectra
        for t in self.tf:
            t.Plot(self.pwd)

    def GetSpectra(self,layer):
        if not self.parser.IsParsed():
            self.PostAnalysis()            
        # Get Spectra from file
        if self.spec.numofspec==0:
            self.parser.GetSpectra(self.spectralist)

        return self.spectralist.GetSubFamilyLayer(layer)
        
             
    def GetTF(self,df):
        if not self.parser.IsParsed():
            self.PostAnalysis()            
        # Get Spectra from file
        if len((self.tf))==0:
            self.parser.GetTF(self.tf)

        for t in self.tf:
            if t.df==df:
                return t
                                
    def CleanWorkDir(self):
        for f in os.listdir(self.pwd):
            filename=os.path.join(self.pwd,f)
            # Remove error files if empty
            if f.endswith('.err'):
                if os.stat(filename)[6]==0:
                    os.remove(filename)
            # Remove output files if empty                
            if f.endswith('.out'):
                if os.stat(filename)[6]==0:
                    os.remove(filename)

    def __del__(self):
        self.CleanWorkDir()

class TransferFunction():
    def __init__(self,freq=[],ampl=[],df=0.0):
        self.npoints=0.0
        self.df=df
        self.SetTF(freq,ampl)

    def SetTF(self,freq,ampl):
        self.SetFrequency(freq)
        self.SetAmplif(ampl)

    def SetFrequency(self,frq):
        self.frequency=np.array(frq,dtype='float64')

    def SetAmplif(self,ampl):
        self.amplification=np.array(ampl,dtype='float64')
                
    def WriteCsv(self,dir,filename=''):
        if not filename:
            root='Amplification_df='
            ext='.csv'
            filename=root+str(self.df)+ext
        fname=os.path.join(dir,filename)
        f=open(fname,'wb')
        writer=csv.writer(f,dialect='excel')
        for j,val in enumerate(self.frequency):
            writer.writerow([self.frequency[j],self.amplification[j]])
        f.close()

    def Plot(self,filename='',ylabel='',show=0,axis=''):
        plt.semilogx(self.frequency,self.amplification)
        plt.xlabel("Frequency")
        if axis:
           plt.axis(axis) 
        
        if not ylabel:
            ylabel="Amplification"
        plt.ylabel(ylabel)
        if show:
            plt.show()
        elif not filename:
            pass
        else:
            plt.savefig(filename, bbox_inches='tight')

    def WriteXls(self):
        raise NotImplementedError("Error : Can't output to xls format for now")        

    def Average(self,newtf):
        '''Update the tf so that the spectra values are the average of the
        present values with those of a new tf passed in argument. For the
        moment, it considers that both tf have the same frequency range
        '''
        if self.numoftf==0:
            self.CopyTf(newtf)
        else:
            if newtf.frequency!=self.frequency:
                raise NotImplementedError('Frequency range must be strictly identical for every spectrum')
                return
            #Loop over the values of the tf
            for idx,val in enumerate(newtf.amplification):
                self.amplification[idx]=(self.numoftf*self.amplification[idx]+val)/(self.numoftf+1)            
        self.numoftf=self.numoftf+1

    def CopyTf(self,tf):
        self.frequency=tf.frequency
        self.amplification=tf.amplification
            
    #### Deprecated ####
    def SetDf(self,delta):
        self.df.append(delta)
    ####################

                    
class FileParser():
    def __init__(self,files):
        self.files=files
        self.parsed=False
        
    def IsParsed(self):
        return self.parsed
        
    def ReadResultFiles(self):    
        self.textinfile=self.ReadFile(self.files.infile)
        self.textoutfile1=self.ReadFile(self.files.outfile1)
        self.textoutfile2=self.ReadFile(self.files.outfile2)
        self.parsed=True
        
    def ReadFile(self,file):
        f=open(file)
        return f.readlines()
        f.close()        
    #Deprecated?    
    def GetRSInfo(self,spec):
        subtext=self.GetSubFile(self.textinfile,9)
        for sub in subtext:
            layer=int(sub[1].split()[0])
            dampings=[float(x) for x in sub[3].split()]
            # THIS HAS TO BE MODIFIED. CREATE A NEW CLASS TO INCLUDE
            # INFO ABOUT THE LAYER.
            spec.InitSpectra(layer,dampings)

    def GetSpectra(self,spectralist):
        subtext=self.GetSubFile(self.textoutfile1,9)
        for sub in subtext:
            for line in sub:
                match=re.search('LAYER NUMBER \s+ (\d+)',line)
                if match:
                    # Add Spectra object to the list of spectra of the
                    # analysis.
                    layer=int(match.group(1))
                match=re.search('\s{5}DAMPING RATIO = (\d+.\d+)\n',line)
                if match:
                    damping=float(match.group(1))
                    frq=[]
                    spectra=[]
                match=re.search('\d+\s+\d+\.\d+\s+\d+\.\d+\s+'+
                                '\d+\.\d+\s+\d+\.\d+\s+(\d+\.\d+)'+
                                '\s+\d+\.\d+\s+(\d+\.\d+)',line)
                if match:
                    spectra.append(float(match.group(1)))
                    frq.append(float(match.group(2)))
                # this appears right after the list of the spectra
                match=re.search('VALUES IN PERIOD',line)
                if match:
                    try:
                        nextspec=ResponseSpectraShake(frq,spectra,\
                                                      damping,layer)
                        spectralist.AddSpectra(nextspec)
                    except NameError:#Can't remember what this is...
                       pass    
        # for spec in spectralist:
        #     print spec.name, spec.damping
            
    def GetTFInfo(self,listoftf):
        pattern='\sdf=(\d\.\d+)'
        for line in self.textinfile:
            match=re.search(pattern,line)
            if match:
                listoftf.append(TransferFunction(float(match.group(1)
                                                       )))
                
    def GetTF(self,listoftf):
        
        self.GetTFInfo(listoftf)
        subtext=self.GetSubFile(self.textoutfile1,10)
        for [idx,sub] in enumerate(subtext): #One function per subtext
            freq=[]
            amp=[]
            for line in sub:
                match=re.search('\s+(\d+\.\d+)\s+(\d+.\d+)',line)
                if match:
                    freq.append(float(match.group(1)))
                    amp.append(float(match.group(2)))
                
            listoftf[idx].SetTF(freq,amp)
                            
    def GetSubFile(self,text,optionnumber):

        search1='OPTION\s+'+str(optionnumber)
        search2='OPTION'
        start=-1;
        stop=-1;
        subtext=[]
        for idx,line in enumerate(text): #loop over the lines
            if re.search(search1,line.upper()):
                if start<0:
                    start=idx+1
                else:
                    stop=idx
                    subtext.append(text[start:stop])
                    start=idx+1
                    stop=-1
            elif start>0 and re.search(search2,line.upper()):
                stop=idx
                subtext.append(text[start:stop])
                start=stop=-1                                
        if start>0:
            stop=idx
            subtext.append(text[start:stop])
                
        return subtext
                
class DataFile():
    def __init__(self,filename):
        fileroot=os.path.splitext(filename)[0]
        self.infile=fileroot+'.in'
        self.outfile1=fileroot+'_1.out'
        self.outfile2=fileroot+'_2.out'

    def Summarize(self):
        '''For Debugging purposes only'''
        print 'Input file:\n'+self.infile+'\n'
        print 'Output file 1:\n'+self.outfile1+'\n'
        print 'Output file 2:\n'+self.outfile2+'\n'

class TimeHistoryShake(TimeHistory):
    def __init__(self,filename=None,fformat=None):
        # Test extension
        [root,ext]=os.path.splitext(filename)
        if ext!='eqc':
            self.filename=root+'.eqc'
        self.motherfile=filename
        super(TimeHistoryShake, self).__init__(filename=filename,\
                                               fformat=fformat)
        
    def ConvertFromThge(self,th,n=8192):
        self.motherfile=th.filename
        self.accel=th.accel
        self.npoints=th.npoints
        self.dt=th.dt
        self.WriteThShake(n)
    
    def WriteThShake(self,n=8192):
        
        '''Write time history in shake format. The parameter n is
        used to specify the number of points that the time-history
        must have. For shake use, it has to be a power of 2. The
        default is set to 8192.'''

        #Extend the time serie if needed :
        if self.npoints!=n:
            self.AdjustLength(n,check=False)
            
        f=open(self.filename,'w')    
        header=self.ShakeHeader()
        f.write(header)
        for i in range(int(math.ceil(self.npoints/8.0))):                
                b=self.accel[i*8:i*8+8]
                self.WriteLine(f,b)    
        f.close()

    def WriteLine(self,f,b):
        '''Write a line of 8 numbers in the file f'''
        for val in np.nditer(b):
            if val>=0:
                f.write('')
            f.write('%9.6f' % val)
        f.write('\n')

    def ShakeHeader(self):
        '''Create Header file for shake accelerogram file'''
        header='Source File: '
        header+=self.motherfile+'\n'
        header+='SHAKE2000 Conversion:'+2*' '
        header+=str(self.npoints)+2*' '
        header+=str(self.dt)+2*' '
        header+='5'+2*' '+'8'+2*' '+'9'+2*' '+'(8f9.6)'+'\n'
        header+="Acceleration Units: (g's) - No. Values: "
        header+=str(self.npoints)+' - Time Step: '
        header+=str(self.dt)+' (secs)\n'
        header+='Data Format: 8f9.6 - No. Header Lines:  5\n'
        header+='SEISME HORIZONTAL\n'
        return header

    

class ResponseSpectraShake(ResponseSpectra):
    def __init__(self,frequency=[],spectra=[],damping=0.0,\
                    layer=0):
        name='Layer_'+str(layer)
        self.layer=layer
        super(ResponseSpectraShake,self).__init__(frequency,spectra,damping,name)
    
class SpectraFamilyShake(SpectraFamily):
    
    def __init__(self,family=[]):
        super(SpectraFamilyShake,self).__init__(family)

    def GetSubFamilyLayer(self,layer):
        speclist=[rs for rs in self.family if rs.layer==layer]
        subfamily=SpectraFamily(speclist)
        return subfamily

    def PlotPerLayer(self,layer,filename='',ylabel='',show=0,axis=''):
        sf=self.GetSubFamilyLayer(layer)
        sf.Plot(filename,ylabel,show,axis)

    def GetSpectraDampingLayer(self,damping,layer):
        sf=self.GetSubFamilyLayer(layer)
        sf=sf.GetSubFamilyDamping(damping)
        if sf.numofspec>1:
            raise Warning('More than one spectra have the specified layer and damping')

        return sf[0]
        
    
def Main():
    th=TimeHistoryShake(filename='./TestDir/000042xa_acc.acc',fformat='acc')
    th.WriteThShake()
    th.Plot(show=1)
            
if __name__=="__main__":
    Main()
