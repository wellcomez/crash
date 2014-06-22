__author__ = 'zhujialai'
symbolmap={}
def addresssymbol(address,module):
    try:
        return symbolmap["%d"%(address)]
    except:
        pass
    import os
    cwd=os.getcwd()
    path={"ksmobilebrowser",cwd+'/archive/ksmobilebrowser.app/ksmobilebrowser'}
    binary_path = path[module]

def dosym(binary_path,base,addresslist):
    import subprocess
    cmd = [
        '/usr/bin/atos',
        '-d',
        '-o', binary_path,
        # '-arch', 'armv7',
        '-l', '0x%x' % base
    ]
    for address in addresslist:
        cmd.append('0x%x' %(address))
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    i = 0
    ret={}
    for line in output.split('\n'):
        if i<len(addresslist):
            try:
                import  string
                if string.atoi(line,16)==addresslist[i]:
                    ret[addresslist[i]]=None
            except:
                ret[addresslist[i]]=line
                pass
        i=i+1
    return ret

def sym0x1000(binary_path,address):
    return  dosym(binary_path,0x1000,address)

class addessinfo(object):
    def __init__(self,adress):
        self.address=adress
        self.symbol=None

class libSymbol(object):
    def __init__(self,name,path):
        self.d={}
        self.miss={}
        self.name=name
        self.path=path
        return
    def find(self,address):
        try:
            return self.d[address].symbol
        except Exception as e:
            a=addessinfo(address)
            self.miss[a.address]=a
            return None
    def symblic(self):
        result=sym0x1000(self.path,self.miss)
        i=0
        for address in self.miss:
            s=self.miss[address]
            try:
                s.symbol=result[i]
                self.d[address]=s
            except:
                pass
            i=i+1
        self.miss={}







class systemSymbol(object):
    def __init__(self):
        self.d={}
        return
    def find(self,module,address):
        try:
            return self.d[module][address]
        except Exception as e:
            return None



class symbolDB(object):
    def __init__(self):
        self.d=dict()
        pass
    def instance(self):
        return self
    def __setitem__(self, key, value):
        self.d[key]=value
    def __getitem__(self, item):
        return self.d[item]

def base0x1000(base,address):
    return address-base+0x1000
if __name__ == "__main__":
    path="/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks/UIKit.framework/UIKit"
    base=0x491B000
    print dosym(path,0x1000,[ base0x1000(base,0x04b749de),0x0])