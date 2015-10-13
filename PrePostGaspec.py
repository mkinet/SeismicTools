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
        
    def GenInfile(self,accfile,template='GaspecTemplate.in'):pass
        # ShakeTemplate file must in the directory where python is
        # running
        
    def RunAnalysis(self):pass
            
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

    def GetSpectra(self,layer):
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
        
    def ReadResultFiles(self):    
        
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
    
class SpectraFamilyGaspec(SpectraFamily):pass
    
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
        
    
def Main():pass
            
if __name__=="__main__":
    Main()
