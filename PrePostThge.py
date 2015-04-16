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
        '''Function to launch THGE.
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

    def GenerInputFile(self,spectra,seed,type='period',\
                        duree=20.480,damping=0.05,srpcheck=False):
        # VDA (02/04/2015): changed input to allow a definition of the
        #      input file either through period-acceleration couples
        #      or through frequency-acceleration couples.
        # MAK (07/04/2015): Improved VDA Implementation for period or
        #      frequency definition
        
        zpa=spectra.GetZPA()
        line=''
        # We can generate two types of input files for THGE, defining
        # the target spectra by period,acceleration, or by
        # frequency,acceleration.
        if type=='period':
            typ=1
            # by convention, period is sorted in descending
            # order. Here, we want it in ascending order, hence, the
            # list is looped from last to first element.
            for idx in range(spectra.npoints-1,-1,-1):
                line+='   %11.3f   %11.3f\n'\
                % (spectra.period[idx],spectra.spectra[idx])
        elif type=='frequency':
            typ=0
            for idx in range(spectra.npoints):
                line+='   %11.3f   %11.3f\n'\
                % (spectra.frequency[idx],spectra.spectra[idx])
        else:
            raise SyntaxError("format of spectrum is badly specified.\
                       Use either type='period', or type='frequency'")		     		 
        # create the text of the file 
        text='%6.3f    %6.3f     1.000     8.000     3.000 \n'%(zpa,duree)
        text+=' 1.100   25\n'
        text+='%7.0f\n 0 0\n'% (seed)
        text+=' %3.0f 0 %1d     %5.3f\n'% (spectra.npoints,typ,damping)
        text+=line
        text+='    -1.000    -1.000\n'
        text+=' %1d     0.200    34.000     1.000\n'% srpcheck
        # write in file.
        f=open(self.inputfile,'w')
        f.write(text)
        f.close()

    def ConvertToShake(self,n=8192):
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
        self.ReadFromAcc(filename)

        
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
    thname='test_thge.png'
    shake_th.Plot(thname,ylabel='Acceleration (g)')
    plt.clf()

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
    thname='test_thge.png'
    shake_th.Plot(thname,ylabel='Acceleration (g)')
    plt.clf()

if __name__=="__main__":
    TestThge()
    #TestThge2()   
