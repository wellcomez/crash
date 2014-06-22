__author__ = 'zhujialai'
import re
import  shelve

#cppfiltsymbolt=shelve.open("cxxfilt")
def demangle(names):
    import subprocess
    import atosl
    output2=atosl.cxxfilt(names,1)
    return output2
    #cmd = [
    #    'c++filt',
    #    '-n'
    #]
    #cmd.append('%s'%(names))
    #output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    #return output[0:len(output)-1]

re_instance_file=re.compile('''\((\w+.\w+):(\d+)\)''')
class func(object):
    def __setattr__(self,a,k):
        if a=="callinfo" and k!=None:
            ddd={"1":"1"}
            if type(k)==type(ddd):
                call=func.callinfo()
                for key in k:
                    if key!='py/object':
                        call.__setattr__(key,k[key])
                k=call
        object.__setattr__(self,a,k)

    class callinfo(object):
        @staticmethod
        def fromdict(dic):
            _self=func.callinfo()
            return _self
        def __init__(self):
            self.METHOD=None
            self.CLASS=None
            self.LAN=None
            self.CALL=None
            pass
        def __repr__(self):
            return ""
    @staticmethod
    def is_cpp(s):
        try:
            result=re.compile("(.*)::(.*)\(.*").findall(s)[0]
            c=func.callinfo()
            c.LAN="CPP"
            c.METHOD=result[1]
            c.CLASS=result[0]
            c.CALL="%s::%s"%(c.CLASS,c.METHOD)
            return c
        except Exception as e:
            return None

    @staticmethod
    def is_c(s):
        ret=func.is_cpp(s)
        if ret!=None:ret
        try:
            c=func.callinfo()
            c.METHOD=re.compile("(\w+) ").findall(s)[0]
            c.LAN="C"
            c.CALL=c.METHOD
            return c
        except Exception as e:return None


    @staticmethod
    def is_cppfilt(s):
        try:
            import re
            if s[0:2]!="_Z":return None
            s=s.split(" ")[0]
            #global cppfiltsymbolt
            try:
                s=demangle(s)
                result=re.compile("(.*)::(.*)\(.*").findall(s)[0]
                print s
                #result=cppfiltsymbolt[s]
                # cppfiltsymbolt.close()
            except:pass
                #key=s
                #cppfiltsymbolt[key]=result
                #cppfiltsymbolt.sync()
                # cppfiltsymbolt.close()


            c=func.callinfo()
            c.LAN="CPP"
            c.METHOD=result[1]
            c.CLASS=result[0]
            c.CALL=c.CLASS+"::"+c.METHOD
            #print s
            return c
        except Exception as e:
            return None
    @staticmethod
    def isUnresolvedC(s):
        black=['<redacted>','CFRunLoopRunInMode','sysSignalHandler','main','objc_exception_throw',"CFRunLoopSourceSignal"]
        try:
            def check(b):
                if s.find(b)==0:
                    _self=func.callinfo()
                    _self.CLASS=None
                    _self.METHOD=s
                    _self.CALL=_self.METHOD
                    _self.LAN="C"
                    return _self
                return None
            for b in black:
                ret=check(b)
                if ret!=None:
                    return ret
        except:return None

    @staticmethod
    def isUnresolved(s):
        try:
            result=re.compile("([\d\w]*)\s.*").findall(s)[0]
            c=func.callinfo()
            c.LAN="C"
            c.METHOD=result[0]
            return c
        except:
            return None

    @staticmethod
    def is_oc(s):
        try:
            import  re
            re_instance_method=re.compile('''[-+]\[(.+) (.+)\]''')
            try:s=s[s.find('-['):len(s)]
            except:
                try:s=[s.find("+["),len(s)]
                except:pass
                pass
            result=re_instance_method.findall(s)[0]
            _self=func.callinfo()
            _self.CLASS=result[0]
            _self.METHOD=result[1]
            _self.LAN="OC"
            _self.CALL=s[0:1]+"[%s %s]"%(_self.CLASS,_self.METHOD)
            return _self
        except Exception as e:return None

    def extractSymblic(self,s):
        import  re
        #'-[LBVideoPlayerView handleNextVideo] (LBVideoPlayerView.m:3353)'
        try:
            result=re_instance_file.findall(s)[0]
            self.FILE=result[0]
            self.LINE=result[1]
            self.OFFSET_TYPE="SRC"
        except Exception as e:pass
        if self.OFFSET_TYPE==None:
            try:
                R=s.split("+")
                self.FILE=R[0]
                self.LINE=R[1]
                self.OFFSET_TYPE="BIN"
            except Exception as e:
                #print "cant resolve offset %s "%(s)
                pass

        self.callinfo=func.is_oc(s)
        if self.callinfo!=None:return

        self.callinfo=func.is_cpp(s)
        if self.callinfo!=None:return

        self.callinfo=func.is_cppfilt(s)
        if self.callinfo!=None:return

        self.callinfo=func.isUnresolved(s)
        if self.callinfo!=None:return

        #if resovled==True:return
        #try:
        #    if self.OFFSET_TYPE=="BIN":
        #        result=re.compile("_ZN\d+(WebCore)(\d+\w+)").findall(s)[0]
        #        print s
        #        self.LAN="CPP"
        #        resovled=True
        #except Exception as e:pass

        #print "Cant't resolve method (",s,")"
        return

    def __init__(self):
        self.FILE=None
        self.LINE=None
        self.OFFSET_TYPE=None
        return


class frame(object):
    def __init__(self,f):
        #{'symbolic': 'objc_exception_throw + 38', 'id': 1, 'module': 'libobjc.A.dylib', 'address': 973854407}
        self.id=f['id']
        self.function = func()
        self.function.module=f['module']
        self.address=f["address"]
        self.symblic=f['symbolic']
        self.function.extractSymblic(self.symblic)
        #print self
        return
    def json(self):
        pass


class stack(object):
    def __init__(self,s):
        self.frames=[]
        for f in s:
            #print f
            self.frames.append(frame(f))
        #print self
        return
    def add(self,frame):
        self.list[frame.id]=frame
    def json(self):
        frames=[]
        for frame in self.frames:
            m=frame.function.module
            a=frame.address
            f=frame.symblic
            frames.append({"a":a,"m":m,"f":f})
            pass
        import jsonpickle
        return jsonpickle.encode(frames)
def md5(s):
    import hashlib
    return hashlib.md5(s).hexdigest()
class crash(object):
    @staticmethod
    def load(s):
        import jsonpickle
        c=jsonpickle.decode(s)
        return c
    def save(self,pwd):
        import os
        f=os.path.join(pwd,self.id)+'.json'
        import jsonpickle
        s=jsonpickle.encode(self)
        open(f,'w').write(s)
        return f
    def __init__(self,dic):
        #print 1
        try:
            self.did=dic['did']
        except:
            pass
        #print 2
        self.reason=dic['reason']
        #print 3
        self.version=dic['version']
        #print 4,dic['call_stack']
        self.stack=stack(dic['call_stack'])
        #print 5
        self.device_info=dic['device_info']
        #print 6
        import os

        self.id=dic['path']
        #print 7
        self.id=os.path.basename(self.id)
        #print 8
        self.date=dic['date']
        #print 9
        self.dir=self.date
        return

import json
class MyEncoder(json.JSONEncoder):
    def default(self,obj):
        #convert object to a dict
        d = {}
        d['__class__'] = obj.__class__.__name__
        d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d


class MyDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self,object_hook=self.dict2object)
    def dict2object(self,d):
        #convert dict to object
        if'__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name)
            class_ = getattr(module,class_name)
            args = dict((key.encode('ascii'), value) for key, value in d.items()) #get args
            inst = class_(**args) #create new instance
        else:
            inst = d
        return inst

def test():
    t={'path':"",
        'count': 1,
        'date':"1",
      'reason': '*** -[__NSArrayM objectAtIndex:]: index 3 beyond bounds for empty array', 'version': '1.7.8777.406',
      'call_stack': [{'symbolic': 'objc_exception_throw + 38', 'id': 1, 'module': 'libobjc.A.dylib', 'address': 973854407}, {'symbolic': '<redacted> + 232', 'id': 2, 'module': 'CoreFoundation', 'address': 802135653}, {'symbolic': 'ksmobilebrowser + 776499', 'id': 3, 'module': 'ksmobilebrowser', 'address': 780595}, {'symbolic': 'ksmobilebrowser + 777099', 'id': 4, 'module': 'ksmobilebrowser', 'address': 781195}, {'symbolic': 'ksmobilebrowser + 793623', 'id': 5, 'module': 'ksmobilebrowser', 'address': 797719}, {'symbolic': '<redacted> + 12', 'id': 6, 'module': 'CoreFoundation', 'address': 802709113}, {'symbolic': '_CFXNotificationPost + 1720', 'id': 7, 'module': 'CoreFoundation', 'address': 802134913}, {'symbolic': '<redacted> + 4084', 'id': 8, 'module': 'AVFoundation', 'address': 784280937}, {'symbolic': '<redacted> + 10', 'id': 9, 'module': 'libdispatch.dylib', 'address': 978985219}, {'symbolic': '<redacted> + 22', 'id': 10, 'module': 'libdispatch.dylib', 'address': 978985199}, {'symbolic': '_dispatch_main_queue_callback_4CF + 268', 'id': 11, 'module': 'libdispatch.dylib', 'address': 978995625}, {'symbolic': '<redacted> + 8', 'id': 12, 'module': 'CoreFoundation', 'address': 802743737}, {'symbolic': '<redacted> + 1308', 'id': 13, 'module': 'CoreFoundation', 'address': 802737797}, {'symbolic': 'CFRunLoopRunSpecific + 524', 'id': 14, 'module': 'CoreFoundation', 'address': 802125121}, {'symbolic': 'CFRunLoopRunInMode + 106', 'id': 15, 'module': 'CoreFoundation', 'address': 802124579}, {'symbolic': 'GSEventRunModal + 138', 'id': 16, 'module': 'GraphicsServices', 'address': 883090155}, {'symbolic': 'UIApplicationMain + 1136', 'id': 17, 'module': 'UIKit', 'address': 844816869}, {'symbolic': 'ksmobilebrowser + 39135', 'id': 18, 'module': 'ksmobilebrowser', 'address': 43231}, {'symbolic': 'ksmobilebrowser + 26984', 'id': 19, 'module': 'ksmobilebrowser', 'address': 31080}], 'device_info': {'device': {'iPhone5,4': 1}, 'nojb': 1, 'os': {'7.0': 1}, 'jb': 0}, 'base_address': 4096}
    c=crash(t)
    import json
    def f(obj):
        d=obj.__dict__;
        pass
    json.dumps(c,default=f)

    import jsonpickle
    e=jsonpickle.encode(c)
    c=crash.load(e)
    for frame in c.stack.frames:
        print frame.function.callinfo
    #func().extractSymblic('-[LBVideoPlayerView handleNextVideo] (LBVideoPlayerView.m:3353)')
    d="-[QVVideoPlayerViewController initWithDelegate:dataSource:playIndex:]"
    #func().extractSymblic(d)
    d="__80-[QvodPlayerViewController(private) createPlayViewControllerIfNeedAndPlayIndex:]_block_invoke172 (QvodPlayerViewController.m:255)"
    #func().extractSymblic(d)
    d="CFFmpegDemuxer::FixFileSizeFromP2P() (FFmpegDemuxer.cpp:650)"
    d="sysSignalHandler (YrCrashLogger.m:313)"
    d="_ZN7WebCore4Page8goToItemEPNS_11HistoryItemENS_13FrameLoadTypeE + 56"
    func().extractSymblic('_ZN7WebCore14ResourceHandle25loadResourceSynchronouslyEPNS_17NetworkingContextERKNS_15ResourceRequestENS_17StoredCredentialsERNS_13ResourceErrorERNS_16ResourceResponseERN3WTF6VectorIcLm0ENSB_15CrashOnOverflowEEE + 394')

if __name__ == "__main__":
    func().extractSymblic('_ZN7WebCore14ResourceHandle25loadResourceSynchronouslyEPNS_17NetworkingContextERKNS_15ResourceRequestENS_17StoredCredentialsERNS_13ResourceErrorERNS_16ResourceResponseERN3WTF6VectorIcLm0ENSB_15CrashOnOverflowEEE + 394')
    pass
    #d="_ZN3JSC8evaluateEPNS_9ExecStateERKNS_10SourceCodeENS_7JSValueEPS5_ + 426"
    #d="_ZN12DispatchHost17performInvocationEPKv + 12 CFNetwork"
    #d="__70-[QVFilesVideoPlayerController initWithUrlArray:playIndex:completion:]_block_invoke_2 (QVFilesVideoPlayerController.m:549)"
    #func.is_c(d)
    #func().extractSymblic(d)
    #func.is_cppfilt("_ZN7WebCore4Page8goToItemEPNS_11HistoryItemENS_13FrameLoadTypeE + 60")
    #print demangle("_ZN7WebCore4Page8goToItemEPNS_11HistoryItemENS_13FrameLoadTypeE")
    #print(type(dict))
    #test()

