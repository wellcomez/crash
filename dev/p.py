list=[]
if __name__ == "__main__":
    import globalconfig
    import os
    import sys
    import logparser
    try:
        dir=sys.argv[1]
    except:
        dir="config.ini.2.1.9762.532"
    config=globalconfig.globalconfig(os.path.join(os.getcwd(),dir))
    has={}
    for version in config.versionlist:
        p=logparser.logparser(config,version)
        for day in config.generate_date_list():
            import download
            if download.down(day)==False:
                print "notfile"
                try:
                    if has[day]==True:
                        print "hasfile2"
                        pass
                    else:
                        continue
                except:
                    continue
            else:
                print "hasfile"
                has[day]=True
            def cb(c,f):
                import sql
                print f
                sql.sql.connect().insertCrashLog(c)
            #p.pareseLogAtDay(day,cb)
