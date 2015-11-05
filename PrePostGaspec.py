import re
from subprocess import call
from SeismicTools import *
gaspec='C:/Programs/Gaspec/gaspec.exe'

class Analysis():
    def __init__(self,amo=None,pwd=None,name=None,case=None,THinputlist=[]):
        # Damping is needed
        if amo==None:
            print('WARNING: At least one damping value should be\
             specified. A damping of 5% is used by default.')
            amo=[0.05]
        self.amo=amo
        #Get working directory : Working directory is set to be the
        #directory where the script is executed
        if pwd==None:
            pwd=os.getcwd()
        self.pwd=pwd
        # Name of the analysis.Default to name of the working
        # directory
        if name==None:
            name=self.pwd
        self.name=name        
        if case==None:
            case='CAS'
        self.case=case
        ## Input TH, or family of TH??
        self.accelerograms = TimeHistoryFamily(family=THinputlist)
        # Initialize results. We mainly focus on the set of spectra
        # generated
        self.spectralistout=SpectraFamilyGaspec()
        # Initialize parser. THIS IS USED FOR PPROC.
        #self.parser=FileParser(self.datafiles)
    
    def GenInfile(self,fadd=[],amo=[],multfact=1.0):
        # 1) input file containing analysis name and case name.
        f=open('gaspec.dat','w')
        f.write(self.name+'\n'+self.case+'\n')
        f.close()
        # Use a template or hardcode it?
        # 2)
        fname='gaspec_'+self.name+'_'+self.case+'.dat'
        f=open(fname,'w')
        # Commande START
        f.write('START\n'+self.name+'\n'+self.case+'\n'\
                +'UNIT G\n')
        # Commande FREQUENCE. We set IADD to 0 by default : all
        # previously computed frequencies are kept and we add the
        # frequencies in list fadd
        if len(fadd)>0:
            f.write('FREQUENCES'+9*' '+'0'+5*' '+str(len(fadd))+'\n')
            count=0
            for freq in fadd:
                f.write(str.format("{:10.2f}", freq))        
                count+=1
                if count==7:
                    f.write('\n')
                    count=0
                    
        # Commande AMORTISSEMENTS.
        if len(amo)>0:
            f.write('AMORTISSEMENTS'+4*' '+str(len(amo))+'\n')
            count=0
            for a in amo:
                f.write(str.format("{:10.2f}", a))        
                count+=1
                if count==7:
                    f.write('\n')
                    count=0
            if count!=0:f.write('\n')
        # Commande ACCELEROGRAMMES/INPUT.
        f.write('ACCELEROGRAMMES\n')
        # We use default values for IPU and IPL
        # IPU = 0 means there is no output of accelerograms made by
        # GASPEC. IPL = 0 means there is no figure made by GASPEC.
        f.write(str.format("{:15s}",'INPUT')+str.format("{:5d}",0)\
                +'\n')
        # This is a multiplicative factor. We hardcode it to 1.
        f.write(str(multfact)+'\n')
        # Now we need to write the values of the accelerograms :
        for accel in self.accelerograms:
            f.write(str.format("{:5s}",accel.name[0:4])+\
                    str.format("{:5d}",1)+\
                    str.format("{:5d}",1)+\
                    str.format("{:5d}",accel.npoints)+\
                    str.format("{:10.3f}",accel.dt)\
                    +5*' '+'(7F10.2)\n')
            count=0
            for val in accel.accel:
                f.write(str.format("{:10.2f}", val))        
                count+=1
                if count==7:
                    f.write('\n')
                    count=0
            if count!=0:f.write('\n')
        f.write('END\n')
        # # Commande ACCELEROGRAMMES/OUTPUT.
        # # carte 1
        # f.write('ACCELEROGRAMMES\n')
        # # We use default values for IOR, IPU and IPL.
        # # IPU = 1 means output of accelerograms to 80 columns
        # # formatted file. IPL = 0 means there is no figure made by
        # # GASPEC.
        # # carte 2
        # f.write('OUTPUT')
        # # carte 3
        # f.write(str.format("{:5d}",0)+
        #         str.format("{:5d}",1)+
        #         str.format("{:5d}",0)+'\n')
        # # carte 4 et suivantes
        # 
        # # carte 5
        # f.write('END\n')


        # Commande SPECTRES
        # carte 1
        f.write(str.format("{:15s}","SPECTRES")+
                str.format("{:5d}",0)+
                str.format("{:5d}",-1)+
                str.format("{:5d}",0)+
                str.format("{:5d}",0)+'\n')
        # carte 2
        f.write(str.format("{:10.1f}",1.0)+
                str.format("{:20s}",' unites')+
                str.format("{:10.0F}",100.0)+'\n')
        # carte 3 et suivantes
        for accel in self.accelerograms:
            f.write(str.format("{:5s}",accel.name[0:4])+\
                    str.format("{:5d}",1)+\
                    str.format("{:5d}",1)+\
                    str.format("{:5d}",0)+'\n')
        # derniere carte
        f.write('END\n')

        # Commande CHECK
        f.write('CHECK')
        
    def RunAnalysis(self):
        errfile=os.path.join(self.pwd,'gaspec.err')
        err=open(errfile,'w')
        call(gaspec,stdout=err)
        err.close()

    def InitAccel(self,filelist):
        'Initialize Accelerograms through a list of files'
        for filename in filelist:
            
            fname,ext=os.path.splitext(os.path.split(filename)[1])
            if ext != '.csv':
                raise IOError('Accelerograms can only be defined'
                               ' trough csv files')
            TH=TimeHistory(name=fname,filename=filename,fformat='csv')
            self.accelerograms.AddTimeHistory(TH)
            
    def PostSpectra(self,broaden=False):
        '''
        This functions reads the spectra computed by GASPEC,
        corresponding to the accelerograms in input.
        '''
        fname='gaspec_'+self.name+'_'+self.case+'_spacc.dat'
        # 1) test if spacc file exists, if not issue an error.
        # 2) open the file
        try:
            f=open(fname,'r')
        except IOError:
            raise IOError('Something went wrong : Result files\
             does not exist') 
                
        # 3) Loop over the input spectra and search for the name in the
        # output file
        for accel in self.accelerograms:
            pattern=' '+accel.name[0:4]+' '
            for line in f:
                match=re.search(pattern,line)
        # 4) once name is found, read the spectra:                
                if match:
                    # number of values to read
                    nval=int(line.strip().split()[2])
                    freq=[]
                    acc=[[] for x in range(len(self.amo))]
                    for x in range(nval):
                        couple=next(f).strip().split()
                        freq.append(couple[0])
                        for i in (range(len(self.amo))):
                            acc[i].append(couple[i+1])
        # 5) create a spectra object and store it in the family object
                    for i in (range(len(self.amo))):
                        self.spectralistout.AddSpectra(\
                            ResponseSpectra(frequency=freq,\
                                            spectra=acc[i],
                                            damping=self.amo[i],
                                            name=accel.name))
                    #get out of the most inner for loop.
                    break
        # 6) Close the file
        f.close()        
        if broaden:
            self.Broaden()
            
    def WriteSpectraCsv(self):
        # Uses the default filename for now...
        # write results in csv files
        for spectra in self.spectralistout:
             spectra.WriteSpectraCsv(self.pwd)


    def WriteSpectraXls(self):
        filename=self.name+'_'+self.case+'.xls'
        self.spectralistout.WriteSpectraXls(filename=filename)        
            

    def PlotAllSpectra(self,show=0,ylabel='',axis=''):
        '''Plot all spectra in a figure'''
        filename=self.name+'_'+self.case+'_spacc.png'
        self.spectralistout.Plot(dir=self.pwd,
                                 filename=filename,show=show,
                                 ylabel=ylabel,axis=axis)
        plt.clf()


    def PlotIndSpectra(self,show=0,ylabel='',axis=''):
        for spectra in self.spectralistout:
            filename=self.name+'_'+spectra.GetName()\
            +'_D='+str(spectra.damping)+'.png'
            spectra.Plot(filename=filename,show=show,
                                 ylabel=ylabel,axis=axis) 
            plt.clf()
            
    def PlotSpectraDamping(self,damping,filename=None,\
                           ylabel='',show=0, axis=''):pass
                           
        # if filename is None:
        #     filename=self.name+'.png'

        # self.spectralist.PlotPerDamping(damping,filename,ylabel,show,axis)
                                
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
            # Remove Fortran Binary files
            if f.endswith('.78'):
                os.remove(filename)
            # Remove gaspec output files
            if f.endswith('.jnl'):
                os.remove(filename)
            if f=='gaspec.dat':
                os.remove(filename)
            if f.endswith('_spacc.dat'):
                os.remove(filename)
            if f.endswith('.lis'):
                os.remove(filename)                
            if f=='gaspec_TEST_CAS.dat':
                os.remove(filename)
                
    def Broaden(self):
        self.spectralistout.Broaden()
        
    def __del__(self):pass

                            
class FileParser():
    def __init__(self,files):
        self.files=files
        self.parsed=False
        
    def IsParsed(self):
        return self.parsed
        
    def ReadResultFiles(self):    pass
        
    def ReadFile(self,file):
        f=open(file)
        return f.readlines()
        f.close()        

    def GetSpectra(self,spectralist):pass
        # subtext=self.GetSubFile(self.textoutfile1,9)
        # for sub in subtext:
        #     for line in sub:
        #         match=re.search('LAYER NUMBER \s+ (\d+)',line)
        #         if match:
        #             # Add Spectra object to the list of spectra of the
        #             # analysis.
        #             layer=int(match.group(1))
        #         match=re.search('\s{5}DAMPING RATIO = (\d+.\d+)\n',line)
        #         if match:
        #             damping=float(match.group(1))
        #             frq=[]
        #             spectra=[]
        #         match=re.search('\d+\s+\d+\.\d+\s+\d+\.\d+\s+'+
        #                         '\d+\.\d+\s+\d+\.\d+\s+(\d+\.\d+)'+
        #                         '\s+\d+\.\d+\s+(\d+\.\d+)',line)
        #         if match:
        #             spectra.append(float(match.group(1)))
        #             frq.append(float(match.group(2)))
        #         # this appears right after the list of the spectra
        #         match=re.search('VALUES IN PERIOD',line)
        #         if match:
        #             try:
        #                 nextspec=ResponseSpectraShake(frq,spectra,\
        #                                               damping,layer)
        #                 spectralist.AddSpectra(nextspec)
        #             except NameError:#Can't remember what this is...
        #                pass    
        # # for spec in spectralist:
        # #     print spec.name, spec.damping
            
                

class TimeHistoryGaspec(TimeHistory):
    def __init__(self,accel=[],dt=0.0,time=[],filename=None,\
                 fformat=None,name='E999'):
        super(TimeHistoryGaspec, self).__init__(accel=accel,\
                                                dt=dt,\
                                                time=time,\
                                                filename=filename,\
                                                fformat=fformat,\
                                                name=name)
        

class ResponseSpectraGaspec(ResponseSpectra):pass
    # def __init__(self,frequency=[],spectra=[],damping=0.0,\
    #                 layer=0):
    #     name='Layer_'+str(layer)
    #     self.layer=layer
    #     super(ResponseSpectraShake,self).__init__(frequency,spectra,damping,name)
    
class SpectraFamilyGaspec(SpectraFamily):
    
    def __init__(self,family=[]):
        super(SpectraFamilyGaspec,self).__init__(family)

    def PlotPerDamping(self,damping,filename='',ylabel='',show=0,axis=''):pass
        # sf=self.GetSubFamilyLayer(layer)
        # sf.Plot(filename,ylabel,show,axis)

    def GetSpectraDampingLayer(self,damping,layer):pass
        # sf=self.GetSubFamilyLayer(layer)
        # sf=sf.GetSubFamilyDamping(damping)
        # if sf.numofspec>1:
        #     raise Warning('More than one spectra have the specified layer and damping')
        # return sf[0]
        
    
def Test():
    TH1=TimeHistoryGaspec(name='E1',accel=[0.0,0.1,0.2,0.3,0.2,0.1,0.0,-0.1,-0.2,-0.2,-0.1,0.0,0.6],dt=0.1)
    TH2=TimeHistoryGaspec(name='E2',accel=[0.0,0.1,0.2,0.3,0.2,0.1,0.0,-0.1,-0.2,-0.2,-0.1,0.0,0.6],dt=0.2)
    TH1.WriteTh()
    TH2.WriteTh()
    A1=Analysis(amo=[0.02,0.05],
                name='TEST',
                case='CAS')
    A1.InitAccel(['E1.csv','E2.csv'])
    A1.GenInfile() 
    A1.RunAnalysis()
    A1.PostSpectra(broaden=True)
    A1.WriteSpectraCsv()
    A1.PlotAllSpectra()
    A1.PlotIndSpectra()
    A1.WriteSpectraXls()
            
if __name__=="__main__":
    Test()
