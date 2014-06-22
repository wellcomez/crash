import MySQLdb
import csv
dbinstance=None
def md5(s):
    import hashlib
    return hashlib.md5(s).hexdigest()
from crashdb import *
#CREATE TABLE `test`.`home` (
#  `version` VARCHAR(20) NOT NULL,
#  `count` INT NULL,
#  PRIMARY KEY (`version`));
def crash2log(log):
    import crashdb
    key=crashdb.crashkey(log)
    try:
        did=log.did
    except:
        did="unkonw"
    reason=log.reason

    if key.crashtop==None:t=""
    else:t=key.crashtop

    if key.crashbottom==None:b=""
    else:b=key.crashbottom

    file=log.id
    if t!=None:
        t_hash=crashdb.md5(t)
    else:
        t_hash=crashdb.md5(file)
    date=int(log.date)
    os=log.device_info['os']
    jb=log.device_info['jb']
    version=log.version
    id=crashdb.md5(file)
    stack=log.stack.json()
    c_hash=md5(key.symblicChain)
    reason=log.reason
    return [jb,did,t,t_hash,id,c_hash,file,date,os,version,reason]

class log(object):
    def __init__(self,version,conn):
        self.version=version
        self.conn=conn
        self.talbe="`log.%s`"%(version)
        sql='''CREATE TABLE %s (
          `jb` tinyint(4) DEFAULT NULL,
          `did` varchar(64) DEFAULT NULL,
          `t` text,
          `t_hash` varchar(32) DEFAULT NULL,
          `id` varchar(32) NOT NULL,
          `c_hash` varchar(32) DEFAULT NULL,
          `file` varchar(128) DEFAULT NULL,
          `date` varchar(8) DEFAULT NULL,
          `os` varchar(8) DEFAULT NULL,
          `version` varchar(20) DEFAULT NULL,
          `reason` text,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;'''%(self.talbe)
        try:
            self.conn.cursor().execute(sql)
        except:
            pass
    def dogroupTrac(self,version):
        sql='''SELECT t,COUNT(*),date,reason from %s  group BY t_hash'''%(self.talbe)
        cur=self.conn.cursor()
        ret=cur.execute(sql)
        if ret>0:
            result=cur.fetchall()
            ret=[]
            for r in result:
                t=r[0]
                count=r[1]
                date=r[2]
                reason=r[3]
                ret.append({"count":int(count),"trac":t,"reason":reason,"date":date})
            ret = sorted(ret, key = lambda x:x['count'], reverse = True)
            return ret
        else:
            return []
    def getDailyCrash(self,version,function=None):
        cur=self.conn.cursor()
        try:
            sql="SELECT count(*),date FROM %s  where t_hash='%s' group BY date"%(self.talbe,md5(function))
            ret=cur.execute(sql)
        except Exception as e:
            print e
        result=cur.fetchall()
        ret={}
        for r in result:
            count=r[0]
            date=r[1]
            ret[date]=count
        return ret
    def findFunciton(self,function,tag="t",version='1.7.8777.406',unique=True):
        cur=self.conn.cursor()
        if unique==True:
            sql="SELECT file,os,count(*),reason FROM %s  where t_hash='%s' group BY c_hash"%(self.talbe,md5(function))
            ret=cur.execute(sql)
        else:
            sql="SELECT file,os FROM %s  where t_hash='%s'"%(self.talbe,md5(function))
            ret=cur.execute(sql)
        result=cur.fetchall()
        ret=[]
        for r in result:
            file=r[0]
            os=r[1]
            if unique==False:
                ret.append({'id':file,'os':os})
            else:
                #stack=r[2]
                count=r[2]
                reason=r[3]
                #ret.append({'id':file,'os':os})
                ret.append({'id':file,'os':os,'stack':'stack',"count":count,"reason":reason})
        if unique:
            ret = sorted(ret, key = lambda x:x['count'], reverse = True)
        return ret
    def readlogfile(self,logname,version):
        #stacklog.append({"stack":stack,"reason":log.reason,"count":len(stack),"device":ret2,"data":"".join(s)})
        try:
            cur=self.conn.cursor()
            sql="SELECT file,date,version FROM %s  where id='%s'"%(self.talbe,md5(logname))
            ret=cur.execute(sql)
            result=cur.fetchone()
            version=result[2]

            import globalconfig
            import os
            ccc=globalconfig.globalconfig(os.path.join(os.getcwd(),'config.ini.'+version))

            date=result[1]
            dir=os.path.join(ccc.logjson,date)
            file=os.path.join(dir,logname)
            file=open(file+".json")
            s=file.read()
            return s
        except Exception as e:
            print e
            raise  e
    def findLog(self,logname,version='1.7.8777.406'):
        #stacklog.append({"stack":stack,"reason":log.reason,"count":len(stack),"device":ret2,"data":"".join(s)})
        try:
            s=self.readlogfile(logname,version)
            import crash
            import crashdb
            c=crash.crash.load(s)
            os="11"
            reason=c.reason
            stack=c.stack.json()
            return {"id":md5(logname),"os":os,"stack":stack,"reason":reason}
        except Exception as e:
            print e
            raise  e
    def importFromCSV(self,file):
        cur=self.conn.cursor()
        sql='''LOAD DATA INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY "," ENCLOSED BY '"' LINES  TERMINATED BY "\r\n"'''%(file,self.talbe)
        print file,sql
        cur.execute(sql)
class logcsv(object):
    def __init__(self,version):
        try:
            self.version=version
            import csv
            import globalconfig
            self.tag='db_%s'%()
            #self.head=["jb","did","t","t_hash","id","c_hash","file","date","os","version","reason"]
            fn="/tmp/%s"%('%s_%s_%s.csv'%(self.tag,globalconfig.now(),version))
            self.csvfile = file(fn, 'wb')
            self.writer = csv.writer(self.csvfile)
            #self.add(self.head)
        except Exception as e:
            print e
    def add(self,row):
        self.writer.writerow(row)
    def close(self):
        self.csvfile.close()
    def import2db(self,dir=None):
        import os
        if dir==None:
            dir="/tmp"
        for file in os.listdir(dir):
            if file.startswith("db_"):
                try:
                    if file.index(self.version)!=-1:
                        f=os.path.join(dir,file)
                        log(self.version,sql.instance().conn).importFromCSV(f)
                        try:
                            import  shutil
                            dst=os.path.join(globalconfig.tmp,"_"+file)
                            shutil.move(f,dst)
                        except Exception as e:
                            print e
                        print "import %s"%(file)
                except Exception as e:
                    print e
    @staticmethod
    def progressnewcsv():
        import os
        dir="/tmp"
        for file in os.listdir(dir):
            if file.startswith("db_"):
                try:
                    r=file.split('_')
                    version=r[len(r)-1].split('.')[0]
                    f=os.path.join(dir,file)
                    def remove(file,tag):
                        try:
                            import  shutil
                            dst=os.path.join(globalconfig.tmp,tag+file)
                            shutil.move(f,dst)
                        except Exception as e:
                            print e

                    log(version,sql.instance().conn).importFromCSV(f)
                    remove(file,"_error")
                    print "import %s"%(file)
                except Exception as e:
                    remove(file,"_")
                    print e

class home(object):
    def __init__(self,conn):
        self.cur=conn.cursor()
    def updateall(self,rets):
        #ret.append({"version":version,"count":count})
        values=[]
        for ret in rets:
            version=ret['version']
            version=str(version)
            count=ret['count']
            try:
                self.cur.execute("insert home values('%s',%d)"%(version,count))
            except Exception as e:
                try:
                    s=self.cur.execute("Update home SET count=%d where version='%s'"%(count,version))
                except Exception as E:
                    pass
                pass
        pass
    def all(self):
        self.cur.execute("SELECT * from home")
        ret=[]
        for r in self.cur.fetchall():
            version=r[0]
            count=r[1]
            ret.append({"version":version,"count":count})
        return ret
class VersionGroup(object):
    def __init__(self,conn,version):
        self.cur=conn.cursor()
        self.version=version
    def updateall(self,rets):
        values=[]
        #ret.append({"count":int(count),"trac":t,"reason":reason,"date":date})
        for ret in rets:
            version=self.version
            version=str(version)
            count=ret['count']
            reason=ret['reason']
            trac=ret['trac']
            date=ret['date']
            t_hash=md5(trac)
            try:
                sql="insert VersionGroup values(%d,'%s','%s','%s',%d,'%s')"%(count,trac,t_hash,reason,int(date),version);
                self.cur.execute(sql)
            except Exception as e:
                try:
                    #s=self.cur.execute("Update VersionGroup SET count='%d' where version='%s'"%(count,version))
                    sql="Update test.VersionGroup SET count=%d where version='%s' and t_hash='%s'"%(count,version,t_hash)
                    self.cur.execute(sql)
                    pass
                except Exception as E:
                    pass
                pass
        pass
    def findFuncitonCount(self,function):
        cur=self.cur
        try:
            ret=cur.execute("SELECT count,reason,date FROM VersionGroup  where t_hash='%s'"%(md5(function)))
        except Exception as e:
            raise  e

        result=cur.fetchall()
        ret=[]
        for r in result:
            count=r[0]
            reason=r[1]
            date=r[2]
            ret.append({"count":count,"date":date,"reason":reason})
        return ret
    def all(self):
        #count,trac,reason,int(date),version
        self.cur.execute("SELECT count,trac,reason,date from VersionGroup where version='%s'"%(self.version))
        ret=[]
        for r in self.cur.fetchall():
            count=r[0]
            trac=r[1]
            reason=r[2]
            date=r[3]
            try:
                ret.append({"version":self.version,
                            "count":count,
                            "trac":trac,
                            "reason":reason,
                            "date":date,"hash":md5(trac)})
            except Exception as e:
                print e
        return ret
import csv
class DailyCrash(object):
    def __init__(self,conn,version):
        self.csvfile = file('%s_%s.csv'%(str(type(self)),version), 'wb')
        self.conn=conn
        self.cur=conn.cursor()

        self.tb="`dailycrash%s`"%(version)
        sql='''CREATE TABLE %s (
              `id` VARCHAR(32) NULL,
              `trac` TEXT NULL,
              `t_hash` VARCHAR(32) NULL,
              `count` INT NULL,
              `date` INT NULL);'''%(self.tb)
        try:
            self.cur.execute(sql)
        except Exception as e:
            pass
        self.version=version

    def insert(self,trac,date,count):
        try:
            if type(date)==type(""):
                date=int(date)
            sql="insert %s values('%s','%s','%s',%d,%d)"%(self.tb,md5(trac+str(date)+self.version),trac,md5(trac),count,date);
            self.cur.execute(sql)
        except Exception as e:
            try:
                #s=self.cur.execute("Update VersionGroup SET count='%d' where version='%s'"%(count,version))
                sql="Update %s SET count=%d where t_hash='%s'"%(self.tb,count)
                self.cur.execute(sql)
                pass
            except Exception as E:
                pass
            pass
    def updateall(self):
        import csv
        csvfile = file('csv_test.csv', 'wb')
        writer = csv.writer(csvfile)
        result=sql.instance().dumpstack(self.version)
        for r in result:
            trac=r['trac']
            dict=sql.instance().getDailyCrash(self.version,trac)
            for r in dict:
                date=r
                count=dict[str(date)]
                row=[md5(trac+str(date)+self.version),trac,md5(trac),count,date]
                writer.writerow(row)
        csvfile.close()
        pass
class trac(object):
    def __init__(self,version,conn=None):
        self.version=version
        if conn!=None:
            self.conn=conn
            self.cur=conn.cursor()
        self.tb="`trac%s`"%(version)
        try:
            sql='''CREATE TABLE %s (
              `date` int(11) NULL DEFAULT NULL,
              `count` int(11) DEFAULT NULL,
              `fixed` tinyint(4) DEFAULT NULL,
              `version` varchar(45) DEFAULT NULL,
              `t_hash` varchar(32) NOT NULL,
              `c_hash` varchar(32) NOT NULL,
              `trac` TEXT NULL,
              `reason` TEXT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;'''%(self.tb)
            self.cur.execute(sql)
        except Exception as e:
            pass
        self.buffer={}
        self.commitThreshHold=0

    def find(self,crash):
        key=self.key(crash)
        t_hash=md5(key.crashtop)
        c_hash=md5(key.symblicChain)
        return self.sqlfind(t_hash,c_hash)

    def sqlFindExisted(self,t_hash,c_hash):
        try:
            ret=self.cur.execute("SELECT count,date from %s where t_hash='%s'"%(self.tb,
                                                                                           t_hash,
                                                                                           ));
            result=self.cur.fetchone()
            if ret==0:
                return None
            else:
                return {"count":result[0],"date":result[1]}
        except Exception as e:
            pass
        return None
    def key(self,crash):
        c=crash
        import crashdb
        key=crashdb.crashkey(c)
        if key.crashtop==None:key.crashtop=""
        if key.symblicChain==None:key.symblicChain=""
        return key
    def c_hash(self,crash):
        c=crash
        import crashdb
        key=crashdb.crashkey(c)
        t=key.symblicChain
        t=md5(t)
        return t

    def udpateCount(self,crash,count):
        key=self.key(crash)
        t_hash=md5(key.crashtop)
        c_hash=md5(key.symblicChain)
        return self.sqlupdatecount(t_hash,c_hash,count)
    def __committodb(self,force=False):
        if force==False:
            if self.commitThreshHold<1000:
                return
        self.commitThreshHold=0
        import progress
        t=progress.tc()
        u=[]
        c=[]
        b2={}
        for key in self.buffer:
            update=self.buffer[key][1]
            data=self.buffer[key][0]
            if update:
                u.append(data)
                b2[key]=[data,True]
            else:
                b2[key]=[[data[0],data[1],data[4]],True]
                c.append(data)
        try:
            if len(c):
                ret=self.cur.executemany('insert into %s'%(self.tb)+' values(%s,%s,%s,%s,%s,%s,%s,%s)',c)
        except Exception as e:
            print e
            pass
        #print t.end()
        try:
            if len(u):
                #WHERE LastName = 'Wilson'
                ret=self.cur.executemany('update %s '%(self.tb)+' set date=%s ,count=%s where t_hash=%s',u)
        except Exception as e:
            print e
            pass
        self.conn.commit()
        self.buffer=b2
        #print t.end()
    def add(self,crash):
        key=self.key(crash)
        t_hash=md5(key.crashtop)
        c_hash=md5(key.symblicChain)
        date=crash.date
        version=crash.version
        trac=key.crashtop
        reason=crash.reason
        added=False
        bufferkey=t_hash
        try:
            c=self.buffer[bufferkey]
            c[0][1]=c[0][1]+1
            c[0][0]=min(c[0][0],date)
        except:
            added=True
            result=self.sqlFindExisted(t_hash,c_hash)
            update=True
            if result==None:
                count=0
                update=False
                c=[[int(date),count+1,0,version,t_hash,"",trac,reason],update]
            else:
                date=min(int(result['date']),date)
                count=result['count']
                c=[[int(date),count+1,t_hash],update]
            pass
        self.commitThreshHold=self.commitThreshHold+1
        self.buffer[bufferkey]=c
        self.__committodb()
        return added
    def close(self):
        self.__committodb(True)
    def sqladd(self,crash):
        key=self.key(crash)
        result=self.sqlfindCount(md5(key.crashtop),md5(key.symblicChain))
        if result:
            count=result
            self.udpateCount(crash,count)
        else:
            self.insert(crash)
            return True
        return False



class logdata(object):
    def __init__(self,version,conn=None):
        if conn!=None:
            self.conn=conn
            self.cur=conn.cursor()

        self.tb="`stack%s`"%(version)
        sql='''CREATE TABLE %s (
              `id` VARCHAR(32) NULL,
              `data` TEXT NULL,
              `t_hash` VARCHAR(32) NULL,
              `stack` TEXT NULL);'''%(self.tb)
        try:
            self.cur.execute(sql)
        except Exception as e:
            pass
        self.version=version
        self.filename='csv_%s.csv'%(self.tb)
        import csv
        self.csvfile = file('csv_%s.csv'%(self.tb), 'wb')
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(["id","data","t_hash","stack"])
    def close(self):
        self.csvfile.close()
    def insert(self,crash):
        c=crash
        import crashdb
        key=crashdb.crashkey(c)
        t=key.crashtop
        if t==None:
            t="unknown"
        import jsonpickle
        row=[md5(c.id),jsonpickle.encode(c),md5(t),c.stack.json()]
        self.writer.writerow(row)
        pass
    def updateall(self,crashlist=None):
        if crashlist==None:
            crashlist=sql.instance().dumpstack(self.version)
        for crash in crashlist:
            c=crash
            import crashdb
            key=crashdb.crashkey(c)
            t=key.crashtop
            if t==None:
                t="unknown"
            import jsonpickle
            row=[md5(c.id),jsonpickle.encode(c),md5(t),c.stack.json()]
            self.writer.writerow(row)
        pass


class sql(object):
    @staticmethod
    def instance():
        global dbinstance
        if dbinstance!=None:
            return dbinstance
        dbinstance=sql()
        return dbinstance;
    @staticmethod
    def connect():
        return sql()
    def __init__(self):
        self.logtable={}
        try:
            self.conn=MySQLdb.connect(host='localhost',user='root',passwd='',db='test',port=3306)
            cur=self.conn.cursor()
            self.insertBuffer=[]
            #self.log=log("",cur)
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def close(self):
        if len(self.insertBuffer):
            self.__insertCrashLog(self.insertBuffer)
        self.commit()
        self.conn.close()
        self.conn=None

    def __del__(self):
        self.close()

    def findlog(self,id):
        sql="SELECT id FROM test.log  where id='%s'"%(id)
        ret=self.conn.cursor().execute(sql)
        if ret>0:return True
        else:return False
    def findFuncitonCount(self,function):
        l=log(version=version,conn=self.conn)
        return l.findFunciton(version,function)
    def getdailycrashWithVersion(self,version):
        cur=self.conn.cursor()
        try:
            ret=cur.execute("SELECT count(*),date FROM log.%s  where version='%s' group BY date"%(version,version))
        except Exception as e:
            raise  e

        result=cur.fetchall()
        ret={}
        for r in result:
            count=r[0]
            date=r[1]
            ret[date]=count
        return ret
    def getDailyCrash(self,version,function=None):
        l=log(version=version,conn=self.conn)
        return l.getDailyCrash(version,function)
    def findFuncitonWithSameDid(self,function,version='1.7.8777.406'):
        sql="SELECT file,t,did,count(*),os FROM log.%s  where t_hash='%s' group BY did"%(version,md5(function))
        try:
            didid={}
            cur=self.conn.cursor()
            ret=cur.execute(sql)
            result=cur.fetchall()
            u=[]
            for r in result:
                try:
                    file=r[0]
                    t=r[1]
                    did=r[2]
                    count=r[3]
                    os=r[4]
                    u.append({"id":file,"os":os,"user":did,"count":count})
                except Exception as e:
                    print e
                    pass
            u = sorted(u, key = lambda x:x['count'], reverse = True)
            return u
        except Exception as e:
            return []
    def didcollection_names(self):
        cur=self.conn.cursor()
        ret=cur.execute("SELECT version,count(*) FROM test.log  group BY version")
        result=cur.fetchall()
        ret=[]
        for r in result:
            version=r[0]
            count=r[1]
            ret.append({"version":version,"count":count})
        return ret
    def collection_names(self):
        return home(self.conn).all()
    def findLog(self,logname,version='1.7.8777.406'):
        #stacklog.append({"stack":stack,"reason":log.reason,"count":len(stack),"device":ret2,"data":"".join(s)})
        try:
            cur=self.conn.cursor()
            sql="SELECT file,date,version FROM log.%s  where id='%s'"%(version,md5(logname))
            ret=cur.execute(sql)
            result=cur.fetchone()
            version=result[2]

            import globalconfig
            import os
            ccc=globalconfig.globalconfig(os.path.join(os.getcwd(),'config.ini.'+version))

            date=result[1]
            dir=os.path.join(ccc.logjson,date)
            file=os.path.join(dir,logname)
            file=open(file+".json")
            s=file.read()
                #print(time.time()-b)
            import crash
            import crashdb
            c=crash.crash.load(s)
            os="11"
            reason=c.reason
            stack=c.stack.json()
            return {"id":md5(logname),"os":os,"stack":stack,"reason":reason}
        except Exception as e:
            print e
            raise  e
    def groupTrac(self,version):
        l=log(version,self.conn)
        result=l.dogroupTrac(self.conn)
        return result
    def dumpstack(self,version):
        import globalconfig
        import os
        ccc=globalconfig.globalconfig(os.path.join(os.getcwd(),'config.ini.'+version))
        sql='''SELECT id,t,version,COUNT(*),date,file FROM `log.%s`  group BY t_hash'''%(version)
        cur=self.conn.cursor()
        ret=cur.execute(sql)
        if ret>0:
            result=cur.fetchall()
            ret=[]
            for r in result:
                i=0
                id=r[0]
                t=r[1]
                version=r[2]
                count=r[3]
                date=r[4]
                file=r[5]
                import time
                b=time.time()
                dir=os.path.join(ccc.logjson,date)
                file=os.path.join(dir,file)
                file=open(file+".json")
                s=file.read()
                #print(time.time()-b)
                import crash
                import crashdb
                c=crash.crash.load(s)
                ret.append([c,t])
            return ret
        else:
            return []
    def sameTrac(self,version,t_hash):
        sql="SELECT t_hash,t,date,reason,stack FROM log.%s  where t_hash=%s group BY c_hash"
        cur=self.conn.cursor(sql,(version,t_hash))
        ret=cur.execute(sql)
        if ret>0:
            ret=cur.fetchall()
            print ret
        else:
            return []
    def __log2sqlvalue(self,log):

        import crashdb
        key=crashdb.crashkey(log)
        cur=self.conn.cursor()
        try:
            did=log.did
        except:
            did="unkonw"
        reason=log.reason

        if key.crashtop==None:t=""
        else:t=key.crashtop

        if key.crashbottom==None:b=""
        else:b=key.crashbottom

        file=log.id
        if t!=None:
            t_hash=crashdb.md5(t)
        else:
            t_hash=crashdb.md5(file)
        date=int(log.date)
        os=log.device_info['os']
        jb=log.device_info['jb']
        version=log.version
        id=crashdb.md5(file)
        stack=log.stack.json()
        c_hash=md5(key.symblicChain)
        return [jb,did,t,t_hash,id,c_hash,file,date,os,version]


    def findCrashlog(self,log):
        pass
    def updateTracCount(self,log):
        import crashdb
        key=crashdb.crashkey(log)
        if key.crashtop==None:t=""
        else:t=key.crashtop
        if t!=None:
            t_hash=crashdb.md5(t)
        else:
            return

        date=int(log.date)
        cur=self.conn.cursor()
        ret=cur.execute("SELECT count from trac where t_hash='%s'"%(t_hash))
        result=cur.fetchone()
        if ret==0:
            self.conn.cursor().execute("insert trac values(%s,%s,%s,%s,%s)",(date,1,0,log.version,t_hash))
        else:
            #count=result[0]+1
            #sql="update trac set count = %s where t_hash = '%s'"%(count,t_hash)
            #self.conn.cursor().execute(sql)
            pass
    def createlogTable(self,version):
        sql='''CREATE TABLE `log.%s` (
          `jb` tinyint(4) DEFAULT NULL,
          `did` varchar(64) DEFAULT NULL,
          `t` text,
          `t_hash` varchar(32) DEFAULT NULL,
          `id` varchar(32) NOT NULL,
          `c_hash` varchar(32) DEFAULT NULL,
          `file` varchar(128) DEFAULT NULL,
          `date` varchar(8) DEFAULT NULL,
          `os` varchar(8) DEFAULT NULL,
          `version` varchar(20) DEFAULT NULL,
          `reason` text,
          PRIMARY KEY (`id`),
          KEY `idx_log_date` (`date`),
          KEY `idx_log_t_hash` (`t_hash`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;'''%(version)
        try:
            if self.logtable[version]==False:
                self.conn.cursor().execute(sql)
            self.logtable[version]=True
        except:pass
    def insertCrashLog(self,log):
        self.createlogTable()
        sqllog=self.__log2sqlvalue(log)
        ret=False
        try:
            cur=self.conn.cursor()
            sql="SELECT id from log where id='%s'"%(md5(log.id))
            ret=cur.execute(sql)
            if ret==0:
                self.insertBuffer.append(sqllog)
                if 1:#len(self.insertBuffer)>100:
                    #print(self.insertBuffer)
                    ret=self.__insertCrashLog(self.insertBuffer,log.version)
                    print "commit .....%d"%(len(self.insertBuffer))
                    self.insertBuffer=[]
            self.updateTracCount(log)
            #print(log.id)
            return True
        except Exception as e:
            print e
            pass
        return ret
    def __insertCrashLog(self,log,version):
        cur=self.conn.cursor()
        sql=""
        list=[]
        multi=False
        try:
            if type(log[0])==type(list):
                multi=True
        except:pass
        if multi:
            ret=cur.executemany('insert into log.%s'%(version)+' values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',log)
        else:
            ret=cur.execute('insert into log values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',log)
        return ret
    def commit(self):
        if len(self.insertBuffer):
            self.__insertCrashLog(self.insertBuffer)
        self.insertBuffer=[]
        self.conn.commit()

if __name__ == "__main__":
    import globalconfig
    import os
    import sys
    try:
        dir=sys.argv[1]
    except:
        dir="config.ini.2.2.10460.667"
    ccc=globalconfig.globalconfig(os.path.join(os.getcwd(),dir))
    f='/Users/acb/Public/Drop Box/crashlogAnalyzer/logjson/20140522/1.8.8856.414_20140522223332___124.205.205.245___1.8.8856.414_2_0x1_0x2.log.json'
    #sql.instance().deleteall()
    #def add():
    #    for day in ccc.generate_date_list():
    #        dir=os.path.join(ccc.logjson,day)
    #        try:
    #            list=os.listdir(dir)
    #        except:list=[]
    #        import time
    #        begin=time.time()
    #        count=0
    #        commitcount=0
    #        if len(list):
    #            for n in list:
    #                file=os.path.join(dir,n)
    #                file=open(file)
    #                s=file.read()
    #                import crash
    #                import crashdb
    #                c=crash.crash.load(s)
    #                insertCount=sql.instance().insertCrashLog(c)
    #                count+=1
    #                print "speed %f"%(count/(time.time()-begin))
    #            sql.instance().commit()
    ##add()
    ##def querytrac():
    ##    sql.instance().groupTrac('2.1.9762.532')
    ###querytrac()



    def updatehome():
        db=sql.instance()
        home(db.conn).updateall(sql.instance().didcollection_names())
        print home(db.conn).all()
    #updatehome()




    def updateTracGroup(verison):
        db=sql.instance()
        group=VersionGroup(db.conn,verison)
        group.updateall(db.dogroupTrac(verison))
    #for version in ccc.versionlist:
    #    updateTracGroup(version)
    #pass

    def testTrac():
        t=trac("test",sql.instance().conn)
        t.sqlinsert(date="1",version="test",t_hash="t_hash",c_hash="c_hash")
        ret=t.sqlfindCount(t_hash="t_hash",c_hash="c_hash")
        t.sqlupdatecount(t_hash="t_hash",c_hash="c_hash",count=ret+1)
    #testTrac()


    def testimport():
        logcsv("2.2.10460.667").import2db()
    #testimport()
    logcsv.progressnewcsv()