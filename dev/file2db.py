__author__ = 'acb'
def loadCrashFromFile(f='/Users/acb/Public/Drop Box/crashlogAnalyzer/logjson/20140522/1.8.8856.414_20140522223332___124.205.205.245___1.8.8856.414_2_0x1_0x2.log.json'):
    #print file
    import crash
    c=crash.load(f)
    for frame in c.stack.frames:
        print frame.function.callinfo
    import crashdb
    key=crashdb.crashkey(c)
    if key.module_crashat():
        print ""
    return c
if __name__ == "__main__":
    import globalconfig
    import os
    import sys
    try:
        dir=sys.argv[1]
    except:
        dir="config.ini.2.2.10460.667"

    handles={}
    handleslogdata={}
    trac={}
    f='/Users/acb/Public/Drop Box/crashlogAnalyzer/logjson/20140522/1.8.8856.414_20140522223332___124.205.205.245___1.8.8856.414_2_0x1_0x2.log.json'
    def parsefile(file):
        file=open(file)
        s=file.read()
        import sql
        import crash
        import crashdb
        try:
            c=crash.crash.load(s)
            #print c.id
        except Exception as e:
            print file,e,s
        try:
            l=handleslogdata[c.version]
        except:
            handleslogdata[c.version]=l=sql.logdata(c.version)
        try:
            h=handles[c.version]
        except:
            handles[c.version]=h=sql.logcsv(c.version)
        try:
            t=trac[c.version]
        except:
            t=trac[c.version]=sql.trac(c.version,sql.sql.instance().conn)
        h.add(sql.crash2log(c))
        if t.add(c):
            l.insert(c)
    def process_configlist():
        ccc=globalconfig.globalconfig(os.path.join(os.getcwd(),dir))
        for day in ccc.generate_date_list():
            dir=os.path.join(ccc.logjson,day)
            try:
                list=os.listdir(dir)
            except:list=[]
            if len(list):
                import time
                begin=time.time()
                count=0
                for n in list:
                    file=os.path.join(dir,n)
                    parsefile(file)
                    count=count+1
                    print "speed %f"%(count/(time.time()-begin))
    def process_newcrash():
        import json
        for f in os.listdir(globalconfig.tmp):
            if f.startswith("newcrash_"):
                print f
                newcrash=os.path.join(globalconfig.tmp,f)
                list=json.load(open(newcrash))
                import progress
                pb=progress.progressbarClass(len(list),"*")
                count=0
                for file in list:
                    parsefile(file)
                    count=count+1
                    pb.progress(count)
                import shutil
                shutil.move(newcrash,os.path.join(globalconfig.tmp,"_"+f))
    process_newcrash()
    for v in handles:
        handles[v].close()
    for v in handleslogdata:
        handleslogdata[v].close()
    for v in trac:
        trac[v].close()
    pass

    import sql
    sql.logcsv.progressnewcsv()
