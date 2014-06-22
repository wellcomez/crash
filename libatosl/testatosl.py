import atosl
print atosl.address('/Users/zhujialai/Downloads/libatosl/ksmobilebrowser',0x1000,0x80000)
print atosl.cxxfilt('_ZN7WebCore4Page8goToItemEPNS_11HistoryItemENS_13FrameLoadTypeE',0)


 #PyRun_SimpleString("import Lazy");  
    #PyRun_SimpleString("Lazy.test()");  
    #PyRun_SimpleString("a = Lazy.TestClass(2, 3)");  
    #PyRun_SimpleString("print dir(a)");  
    #PyRun_SimpleString("a.test()");  
    #PyRun_SimpleString("print 'a.id = ', a.id, ', a.score = ', a.score");  
a=atosl.atosl()
a.test();
a.open("/Users/zhujialai/Downloads/libatosl/ksmobilebrowser");
print a.find(0x80000)
print a.id,a.score
