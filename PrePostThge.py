import  os, math, sys
from subprocess import call
from SeismicTools import *
import PrePostShake
#Location of THGE executable.
thge='C:/Programs/THGE/THGE31.exe'

class ThgeAnalysis():
    def __init__(self,filename):
        self.pwd=os.path.dirname(filename)
        self.inputfile=filename
        fileroot=os.path.splitext(filename)[0]
        self.outputfile=fileroot+'.acc'
        self.th=ThThge(filename=self.outputfile)
        
    def GenerTh(self):
        '''Function to launche THGE.
        Arguments : inputfile : full-path location of inputfile'''
        # Change working directory
        self.CleanBeforeRunning()
        if not os.path.exists(self.inputfile):
            print 'Error: Need to generate input file first'
            raise IOError 
        self.LaunchThge()

    def LaunchThge(self):
        errfile=os.path.join(self.pwd,'thge.err')
        err=open(errfile,'w')
        call([thge,self.inputfile],stdout=err)
        err.close()
        
    def CleanBeforeRunning(self):
        for f in os.listdir(self.pwd):
            filename=os.path.join(self.pwd,f)
            # Remove error files if empty
            if any(filename.endswith(x) for x in ('.out','.err',
                                '.psd','.res','.spe','.trc')):
                    os.remove(filename)
                    
    def GenerInputFile(self,spectra,seed):
        f=open(self.inputfile,'w')
        line=' %s    20.480     1.000     8.000     3.000\n'\
            % str(spectra.spectra[0])
        f.write(line)
        line=' 1.100  25\n'
        f.write(line)
        line=' '+str(seed)+'\n'+' 0 0\n'
        f.write(line)
        line=' '+str(spectra.npoints)+' '+'0 1     0.05\n'
        f.write(line)
        for idx in range(spectra.npoints):
            line=3*' '+str(spectra.period[idx])+5*' '+\
            str(spectra.spectra[idx])+'\n'
            f.write(line)
        line='    -1.000    -1.000\n'
        f.write(line)
        line=' 0     0.100   100.000     1.000\n'
        f.write(line)
        f.close()


    def ConvertToShake(self,n=8192):
        #self.th.ReadFile()
        self.th.SetFromFile(self.outputfile,fformat='thge')
        th_shake=PrePostShake.TimeHistoryShake(self.inputfile)
        th_shake.ConvertFromThge(self.th,n)
        return th_shake
    
    def ReadTargetSpectra(self):pass
        # filename=self.inputfile.splitext()[0]
        # filename=filename+'.spe'
        # # read spectra from file
        # # frq=...
        # # spec=...
        
        # targetspec=ResponseSpectra(frequency=[frq],spectra=[spec],
        #                            damping=0.05,
        #                            name='THGE target spectra')
        # return targetspec
    
class ThThge(TimeHistory):
    def __init__(self,filename=None):
        super(ThThge, self).__init__(filename=filename)
        self.filename=filename
        
    def SetFromFile(self,filename,fformat='csv'):
        options = { None : self.UndefinedFormat,
                    'csv' : self.ReadFromCsv,
                    'acc' : self.ReadFromAcc,
                    'thge' : self.ReadFromThge
                    }
        options[fformat](filename)
                
    def ReadFromThge(self,filename):
        '''read time-history from THGE output'''
        f=open(filename,'r')
        # First line is useless.
        _unused=f.next()
        # Second line contains number of points and timestep
        line=f.next()
        
        dt=float(line.split()[1])
        v=[]
        for x in f:
            v.append(float(x))            
        f.close()
        self.npoints=len(v)
        self.SetTime(dt=dt)
        self.SetValues(v)

        
def GenerTh(fname):
    ''' for tests only '''
    
    A=ThThge()
    A.GenerTh(fname)




def TestThge():
    specfile='./test_thge.txt'
    text='Period (s), SA (g)\n'+\
    '0.000E+00, 3.485E-02\n'+\
    '5.000E-02, 4.989E-02\n'+\    
    '1.000E-01, 7.687E-02\n'+\
    '5.000E-01, 5.176E-02\n'+\
    '2.000E+00, 1.152E-02'
    f=open(specfile,'w')
    f.write(text)
    f.close()
    spectra=ResponseSpectra()
    spectra.ReadFromCsv(specfile,type='period')
    A1=ThgeAnalysis('./test_thge.dat')
    seed=100000
    A1.GenerInputFile(spectra,seed)
    A1.GenerTh()
    shake_th=A1.ConvertToShake(n=3024)
    thname=os.path.join(workdir,name+'_'+case+'.png')
    shake_th.Plot(thname,ylabel='Acceleration (g)')
    SeismicTools.plt.clf()

def TestThge2():
    specfile='./test_thge.txt'
    text='Frequency (s), SA (g)\n'+\
    '.5, 1.152E-02\n'+\
    '2.0, 5.176E-02\n'+\
    '10.0, 7.687E-02\n'+\
    '20.0, 4.989E-02\n'+\
    '35.0, 3.485E-02'
    f=open(specfile,'w')
    f.write(text)
    f.close()
    spectra=ResponseSpectra()
    spectra.ReadFromCsv(specfile,type='frequency')
    A1=ThgeAnalysis('./test_thge.dat')
    seed=100000
    A1.GenerInputFile(spectra,seed,type='frequency')
    A1.GenerTh()
    shake_th=A1.ConvertToShake(n=3024)
    thname=os.path.join(workdir,name+'_'+case+'.png')
    shake_th.Plot(thname,ylabel='Acceleration (g)')
    SeismicTools.plt.clf()

if __name__=="__main__":
    #TestThge()
    TestThge2()   
