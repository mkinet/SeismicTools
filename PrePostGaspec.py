import re
from subprocess import call
from SeismicTools import *
gaspec='C:/Programs/Gaspec/gaspec.exe'

class Analysis():
    def __init__(self,pwd=None,name=None,case=None,THinputlist=[]):
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
    
    def GenInfile(self,fadd=[],amo=[]):
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
        f.write(' 1.\n')
        # Now we need to write the values of the accelerograms :
        for accel in self.accelerograms:
            f.write(#str.format("{:5s}",accel.name)+\
                    str.format("{:5s}","E999")+\
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
            f.write(#str.format("{:5s}",accel.name)+\
                    str.format("{:5s}","E999")+\
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

    def InitAccel(self):pass
        # init accelerograms using definition of TH (through csv files
        # or xls or...)
            
    def GenParamFile(self,fname):pass
        
    def PostAnalysis(self):pass
                
    def PostSpectra(self):pass

    def WriteSpectraCsv(self,dir=os.getcwd()):pass
        # Uses the default filename for now...
        # write results in csv files
        # for spectra in self.spectralist:
        #     spectra.WriteSpectraCsv(dir)

    def WriteSpectraXls(self,filename=None,speclist=None):pass
        # if filename is None:
        #     filename=self.name+'.xls'

        # if speclist is None:
        #     speclist=self.spectralist

        # speclist.WriteSpectraXls(self.pwd,filename)

    def PlotSpectra(self,filename=None,ylabel='',show=0,axis=''):
        if filename is None:
            filename=self.name+'.png'
        self.spectralist.Plot(self.pwd,filename,ylabel,show,axis)

    def PlotSpectraDamping(self,damping,filename=None,\
                           ylabel='',show=0, axis=''):pass
                           
        # if filename is None:
        #     filename=self.name+'.png'

        # self.spectralist.PlotPerDamping(damping,filename,ylabel,show,axis)

    def GetSpectra(self,layer):pass
        # if not self.parser.IsParsed():
        #     self.PostAnalysis()            
        # # Get Spectra from file
        # if self.spec.numofspec==0:
        #     self.parser.GetSpectra(self.spectralist)

        # return self.spectralist.GetSubFamilyLayer(layer)
        
                                
    def CleanWorkDir(self):pass
        # for f in os.listdir(self.pwd):
        #     filename=os.path.join(self.pwd,f)
        #     # Remove error files if empty
        #     if f.endswith('.err'):
        #         if os.stat(filename)[6]==0:
        #             os.remove(filename)
        #     # Remove output files if empty                
        #     if f.endswith('.out'):
        #         if os.stat(filename)[6]==0:
        #             os.remove(filename)

    def __del__(self):pass
#        self.CleanWorkDir()


                    
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
            
                
                                            
class DataFile():
    def __init__(self,filename):pass


    def Summarize(self):
        '''For Debugging purposes only'''
        print 'Input file:\n'+self.infile+'\n'

class TimeHistoryGaspec(TimeHistory):
    def __init__(self,filename=None,fformat=None):pass
        # Test extension
        # [root,ext]=os.path.splitext(filename)
        # if ext!='eqc':
        #     self.filename=root+'.eqc'
        # self.motherfile=filename
        # super(TimeHistoryGaspec, self).__init__(filename=filename,\
        #                                        fformat=fformat)
        
    def ConvertFromThge(self,th,n=8192):pass
        # self.motherfile=th.filename
        # self.accel=th.accel
        # self.npoints=th.npoints
        # self.dt=th.dt
        # self.WriteThShake(n)
    
    def WriteThGaspec(self,n=8192):
        
        '''Write time history in Gaspec format. The parameter n is
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

    def WriteLine(self,f,b):pass
        # '''Write a line of 8 numbers in the file f'''
        # for val in np.nditer(b):
        #     if val>=0:
        #         f.write('')
        #     f.write('%9.6f' % val)
        # f.write('\n')

    def ShakeHeader(self):pass
        # '''Create Header file for shake accelerogram file'''
        # header='Source File: '
        # header+=self.motherfile+'\n'
        # header+='SHAKE2000 Conversion:'+2*' '
        # header+=str(self.npoints)+2*' '
        # header+=str(self.dt)+2*' '
        # header+='5'+2*' '+'8'+2*' '+'9'+2*' '+'(8f9.6)'+'\n'
        # header+="Acceleration Units: (g's) - No. Values: "
        # header+=str(self.npoints)+' - Time Step: '
        # header+=str(self.dt)+' (secs)\n'
        # header+='Data Format: 8f9.6 - No. Header Lines:  5\n'
        # header+='SEISME HORIZONTAL\n'
        # return header


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
        
    
def Main():
    TH1=TimeHistory(accel=[0.0,0.1,0.2,0.3,0.2,0.1,0.0,-0.1,-0.2,-0.2,-0.1,0.0,0.6],dt=0.1)
    A1=Analysis(name='TEST',case='CAS',THinputlist=[TH1])
    A1.GenInfile(amo=[0.02])
    A1.RunAnalysis()
            
if __name__=="__main__":
    Main()
