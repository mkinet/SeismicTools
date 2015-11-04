import ConfigParser,os

class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[default]\n'

    def readline(self):
        if self.sechead:
            try: 
                return self.sechead
            finally: 
                self.sechead = None
        else: 
            return self.fp.readline()

class InputFileParser():
    def __init__(self,filename):
        ## test if filename is path or just a file name
        if not os.path.split(filename)[0]:
            self.cwd = os.getcwd()
            self.infile = os.path.join(self.cwd,filename)
        else:
            self.infile=filename
        self.parser = ConfigParser.ConfigParser()
        self.ParseFile()
        #self.paramvalues = self.ConfigDict()
        
    def ParseFile(self):
        fp=open(self.infile,'r')
        try:
            # need to mark down the init position in the file, in case
            # the [section] keyword is missing.
            pos=fp.tell()
            self.parser.readfp(fp)
        except ConfigParser.MissingSectionHeaderError:
            # go back to beginning of the file
            fp.seek(pos)
            f=FakeSecHead(fp)        
            self.parser.readfp(f)
           
        fp.close()
        self.section=self.parser.sections()[0]

    def GetParamValue(self,param):
        return self.parser.get(self.section,param)
        
## For testing purposes
def Main():
    cwd=os.getcwd()
    file=os.path.join(cwd,"inputtest.in")
    parser = InputFileParser(file)
    name=parser.GetParamValue('nome')
            
if __name__=="__main__":
    Main()
