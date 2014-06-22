__author__ = 'zhujialai'
cantfind=[]

class crashkey(object):
    def __init__(self,c):
        self.crash=c
        self.crashtop=None
        self.crashbottom=None
        s=[]
        for f in self.crash.stack.frames:
            frame=f
            s.append(frame.symblic)
        self.symblicChain="".join(s)
        self.module_crashat()
    def module_crashat(self,module=['ksmobilebrowser']):
        self.crashtop=None
        for i in range(0,len(self.crash.stack.frames)-1):
            frame=self.crash.stack.frames[i]
            try:
                func=frame.function
                call=func.callinfo.CALL
            except Exception as e:
                #print  e
                call=""
            def inlist(l,m):
                for s in m:
                    if s==l:return True
                return False
            if inlist(frame.function.module,module) or inlist(frame.function.module,['WebCore']):
                if call!=None and call!="sysSignalHandler" and len(call)>0:
                    self.crashtop=frame.function.callinfo.CALL
                    break
        self.crashbottom=None
        try:
            for i in range(3,len(self.crash.stack.frames)-1):
                frame=self.crash.stack.frames[len(self.crash.stack.frames)-1-i]
                if inlist(frame.function.module,module):
                    self.crashbottom=frame.function.callinfo.CALL
                    break
        except:pass
        self.symblicChain=""

        for f in self.crash.stack.frames:
            frame=f
            self.symblicChain=self.symblicChain+frame.symblic
        if self.crashtop==None:self.crashtop=""
        if self.crashbottom==None:self.crashbottom=""
        if self.crashbottom==None and  self.crashtop==None:
            #print "++++++++++++++++++++++++++++++++++++++++++++++++++++"
            for f in self.crash.stack.frames:
                frame=f
                #print frame.symblic,frame.function.module
            #if self.crashtop!=None:
            #    print ">>>>>>>>>>>>>",self.crashtop
            #if self.crashbottom!=None:
            #    print "<<<<<<<<<<<<<",self.crashbottom
            #global  cantfind
            #cantfind.append(self.crash)
            return False
        return True

import  pymongo
def md5(s):
    import hashlib
    return hashlib.md5(s).hexdigest()
def object2dict(obj):
    #convert object to a dict
    d = {}
    d['__class__'] = obj.__class__.__name__
    d['__module__'] = obj.__module__
    d.update(obj.__dict__)
    return d
db_trac_indexed={}
class db_trac(object):
    def findOneTrac(self,v,trac):
        r=self.data[v].find_one({"trac_hash":md5(trac)})
        return r
    def updatetracNew(self,version,trac,n):
        if n:n="New"
        else: n=""
        self.data[version].update({"trac_hash":md5(trac)},{"$set": {"new":n }})
    def updateTracReason(self,version,trac,reason):
        self.data[version].update({"trac_hash":md5(trac)},{"$set": {"reason":reason }})
    def incTracCount(self,version,trac):
        self.data[version].update( { "trac_hash": md5(trac) },{ "$inc": { "count": 1 } } )
    def updatetracCount(self,version,trac,n):
        self.data[version].update({"trac_hash":md5(trac)},{"$set": {"count":n }})
    def updatetrac(self,c,k):
        return;
        self.incTracCount(c.version,k.crashtop)
        r=self.findOneTrac(c.version,k.crashtop)
        if r!=None:
            self.incTracCount(c.version,k.crashtop)
            return
        self.data[c.version].insert({"trac":k.crashtop,"count":1,"date":c.date,"version":c.version,"reason":c.reason,"trac_hash":md5(k.crashtop)})
        pass
    def __init__(self):
        self.conn = pymongo.Connection(host='127.0.0.1',port=27017)
        self.data=self.conn.issue
        pass
    def EnableIndexWithField(self,version):
        global db_trac_indexed
        try:
            if db_trac_indexed[version]:return
        except:pass
        #self.data[version].create_index("trac",background=True)
        self.data[version].create_index("trac_hash",background=True)
        db_trac_indexed[version]=True
    def list(self,version='1.7.8777.406'):
        d=self.data[version]
        return  list(d.find(sort=[("count", pymongo.DESCENDING)]))

db_crashlog_indexed={}

class db_logfile(object):
    def findAllLogFileGroupWithFunction(self,function):

        try:
            func = '''
                function(obj, prev)
                {
                    if(prev.log=="n")
                    {
                        prev.log=obj.log;
                        prev.frame=obj.frame;
                        prev.reason=obj.reason;
                    }
                    prev.count++;
                }
               '''
            ret=self.db.group(["c_hash"],{"t_hash":md5(function)},{"count":0,"log":"n","frame":""},func)
            #ret=self.db.find({"t_hash":md5(function)})
            return ret
        except Exception as e:
            print e
            pass
        return []
    def __init__(self,db):
        self.db=db
    def findLogFileWithID(self,ID):
        return None
    def addLogFile(self,c,k):
        import jsonpickle
        frames=[]
        for frame in c.stack.frames:
            m=frame.function.module
            a=frame.address
            f=frame.symblic
            frames.append({"a":a,"m":m,"f":f})
            pass
        self.db.insert({      "id":c.id,
                         "id_hash":md5(c.id),
                             #"log":jsonpickle.encode(c),
                           "frame":jsonpickle.encode(frames),
                               "t":k.crashtop,
                          "t_hash":md5(k.crashtop),
                          "reason":c.reason,
                          "c_hash":md5(k.getTrac)
        })
        return True
class db_crashlog(object):
    def getlog(self):
        l=self.collection_names()
        for v in l:
            db=self.data[v]
            for l in db.find():
                log=l['log']
                import json
                log=json.loads(log)
                l['log']=log
                db.log.insert(l)
                #print l

    def collection_names(self):
        ret=[]
        for r in self.data.collection_names():
            import  re
            try:
                s=re.compile("^\d.(.*)").findall(r)[0][0]
                ss=r.find("logfile")
                if r.find("logfile")>0:pass
                else: ret.append(r)
            except:
                pass
        return ret
    def __init__(self):
        self.conn=None
        pass
    def findLogFileWithID(self,version,ID):
        return db_logfile(self.data[version].logfile).findLogFileWithID(ID)
    def connect(self):
        if self.conn==None:
            self.conn = pymongo.Connection(host='127.0.0.1',port=27017)
            self.data=self.conn.crash
            self.trac=db_trac()
            #self.tracdaily=db_dailycrashcount()
        return  self
    def updatedailycrashWithVersion(self,version):
        pass

    def setdailycrashWithVersion(self,version,result):
        self.data.c[version]["daily"].remove()
        r=self.data.c[version]["daily"].insert({"data":result})

        return
    def getdailycrashWithVersion(self,version):
        try:
            func = '''
                function(obj, prev)
                {
                    if(prev.count==0)
                    {
                        prev.t=obj.t;
                    }
                    prev.count++;
                }
               '''
            db=self.data[version]
            ret={}
            for r in db.group(["date"],None,{"count":0,"t":""},func):
                ret[r['date']]=int(r['count'])
            return ret
        except Exception as e:
            print e
            pass
        return []
    def getdailyFunctionCrashWithVersion(self,version="1.8.8856.414",function=None):
        ret=None
        db=self.data[version]
        result=db.find_one()
        s=result["log"]
        import json
        o=json.loads(s)
        return ret
      
    def hasLogWithID(self,version,ID):
        r=self.data[version].find_one({"id_hash":md5(ID)})
        return r
    def save(self,k,c):
        import  jsonpickle

        import crash
        r=self.hasLogWithID(c.version,c.id)
        if r!=None:return
        self.data[c.version].insert(     {"b":k.crashbottom,
                                          "t":k.crashtop,
                                          "t_hash":md5(k.crashtop),
                                          "c":k.symblicChain,
                                          "date":c.date,
                                          "version":c.version,
                                          "device":c.device_info,
                                          "reason":c.reason,
                                          "id":c.id,
                                          "id_hash":md5(c.id),
                                          "did":c.did

        })
        db_logfile(self.data[c.version].logfile).addLogFile(c,k)
        self.trac.updatetrac(c,k)
    def updatetracCount(self,version,trac):
            n=self.data[version].find({"trac_hash":md5(trac)}).count()
            self.trac.updatetracCount(version,trac,n)
    def dailytopcrash(self,date,version):
        result=list(self.findFuncitonWithContion({"date":date},version=version))
        result = sorted(result, key = lambda x:x['count'], reverse = True)
        return result
    def checknewTrac(self,version):
        for t in self.trac.list(version):
            vv=self.collection_names()
            isNew=True
            for v in vv:
                def aIsLarger(a,b):
                    if a==b:
                        return False
                    if len(a)!=len(b):
                        return False
                    aa=a.split('.')
                    bb=b.split('.')
                    i=0
                    while i<len(aa)-1:
                        j=i;
                        i=i-1
                        if aa[j]>=bb[j]:
                            return True
                    return False
                if aIsLarger(version,v):
                    r=self.trac.findOneTrac(v,t['trac'])
                    if r!=None:
                        isNew=False
                        continue
                else:
                    continue
            self.trac.updatetracNew(version,t['trac'],isNew)
            pass

    def hasLogWithTrac(self,version,trac):
        r=self.data[version].find_one({"t_hash":md5(trac)})
        return r

    def updatealltrac(self,version='1.7.8777.406'):
        for t in self.trac.list(version=version):
            def updatetrac(t):
                r=self.hasLogWithTrac(version,t['trac'])
                if r!=None:
                    reason=r["reason"]
                    self.trac.updateTracReason(version,t['trac'],reason)
            updatetrac(t)

    def EnableIndexWithField(self,version):
        global  db_crashlog_indexed
        try:
            if db_crashlog_indexed[version]:
                return
        except:pass
        self.data[version].create_index("hash_id",background=True)
        self.data[version].create_index("hash_t",background=True)
        db_crashlog_indexed[version]=True

    def findByID(self,version,ID):
        import hashlib
        self.EnableIndexWithField(version)
        result=self.hasLogWithID(version,ID)
        if result!=None:
            return True
        else:
            return False
    def group2(self,version='1.7.8777.406'):
        db=self.data[version]
        result=db.find({"date":"20140305"})
        len=result.count()
        ret={}
        for r in result:
            try:
                t=r["t"]
                b=""
                try:
                    key=t+b
                except:
                    continue
                try:
                    if ret[key]!=None:
                        ret[key]["c"]=ret[key]["c"]+1
                except:
                        import  jsonpickle
                        log=jsonpickle.decode(r['log'])
                        ret[key]={"l":t,"c":1}


            except Exception as e:
                continue
        return ret
    def findLog(self,id,version='1.7.8777.406'):
        try:
            ret=[]
            added={}
            result=self.data[version].find_one({"id_hash":md5(id)})
            return result
        except:
            return None
    def __findFunctionWithTag(self,version='1.7.8777.406',tag="t",function=None,unique=True):
        if tag=="t":
            tag="t_hash"
            function=md5(function)
            try:
                result=self.data[version].find({tag:function})
                return list(result)
            except:
                return []

    def findFuncitonAll(self,function,tag="t",version='1.7.8777.406',unique=True):
        return self.__findFunctionWithTag(version,tag,function,unique)
    def __logfile(self,version):
        return self.data[version].logfile
    def findLogFileWithFunction(self,function,version='1.7.8777.406'):
        return db_logfile(self.__logfile(version)).findAllLogFileGroupWithFunction(function)
    def findFunciton(self,function,tag="t",version='1.7.8777.406',unique=True):
        try:
            ret=[]
            added={}
            result=self.findFuncitonAll(function,tag,version,unique)
            for r in result:
                if unique==False:
                    ret.append({"count":1,"data":r})
                    continue

                found=False
                try:
                    if added[r["c"]]!=None:
                        found=True
                except:pass
                if found==False:
                    added[r["c"]]={"count":1,"data":r}
                else:
                    n=added[r["c"]]["count"]
                    n=n+1
                    added[r["c"]]["count"]=n
            if unique==False:
                return ret;
            for a in added:
                ret.append(added[a])
            return ret
        except:
            return []
    def findFuncitonCount(self,function):
        ret=[]
        for v in db.collection_names():
            r=self.__findFuncitonCount(function=function,version=v)
            if r!=None:
                ret.append(r)
        return ret
    def __findFuncitonCount(self,function,tag="t",version='1.7.8777.406'):
        try:
            ret=[]
            added={}
            r=self.trac.findOneTrac(version,function)
            return  r
        except:
            return None

    def findFuncitonWithSameDid(self,function,version='1.7.8777.406'):
        try:
            didid={}
            result=self.findFuncitonAll(function,"t",version,False)
            for r in result:
                try:
                    import  json
                    s=json.loads(r['log'])['did']
                    if didid[s]!=None:
                        didid[s].append(r)
                except:
                    didid[s]=[]
                    didid[s].append(r)
                    pass
            return didid
        except Exception as e:
            return []
    def countWithCondition(self,condition,version):
        try:
            result=self.data[version].find(condition).count()
            return result
        except Exception as e:
            return 0
    def findFuncitonWithContion(self,condtion,version='1.7.8777.406',enabledid=False):
        try:
            ret=[]
            added={}
            result=self.data[version].find(condtion)
            for r in result:
                found=False
                try:
                    if added[r["t"]]!=None:
                        found=True
                except:pass
                if found==False:
                    added[r["t"]]={"count":1,"data":r}
                else:
                    n=added[r["t"]]["count"]
                    n=n+1
                    added[r["t"]]["count"]=n
            for a in added:
                ret.append(added[a])
            return ret
        except Exception as e:
            return []
    def findNone(self,version='1.7.8777.406'):
        try:
            ret=[]
            samelist={}
            result=self.data[version].find()
            for r in result:
                add=[]
                import  jsonpickle
                log=jsonpickle.decode(r['log'])
                frames=log.stack.frames
                for frame in frames:
                    add.append(frame.symblic)
                ret.append({"address":add,"frame":frames,"chain":r['c'],"log":log})
            commonSet={}
            for r in ret:
                common=None
                commonLen=0
                try:
                    if commonSet[r["chain"]]!=None:
                        continue
                except:
                    pass
                for r2 in ret:
############################################################################################################
                    def longest_common_substring(s1, s2):
                        m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
                        longest, x_longest = 0, 0
                        for x in xrange(1, 1 + len(s1)):
                            for y in xrange(1, 1 + len(s2)):
                                if s1[x - 1] == s2[y - 1]:
                                    m[x][y] = m[x - 1][y - 1] + 1
                                    if m[x][y] > longest:
                                        longest = m[x][y]
                                        x_longest = x
                                else:
                                    m[x][y] = 0

                        return (s1[x_longest - longest: x_longest],x_longest- longest,x_longest)
############################################################################################################
                    if r["chain"]!=r2["chain"]:
                        try:
                            if commonSet[r2["chain"]]!=None:
                                continue
                        except:
                            pass
                        tmp=longest_common_substring(r["address"],r2["address"])
                        if len(tmp[0])>commonLen:
                            commonLen=len(tmp[0])
                            common=tmp
                print  "#####################################################################"
                if common!=None:
                    aa=""
                    if common[1]<3 or common[2]-common[1]==2:
                        #common=None
                        print common,r["chain"]
                        pass
                    else:
                        for frame in r["frame"][common[1]:common[2]]:
                            print "\t",frame.symblic

                        print common,aa
                if common==None:
                    print common,r["chain"]
                commonSet[r["chain"]]=common

            return ret
        except Exception as e:
            print e
            return []
    def getDailyCrash(self,version,function=None):
        try:
            func = '''
                function(obj, prev)
                {
                    if(prev.count==0)
                    {
                        prev.t=obj.t;
                    }
                    prev.count++;
                }
               '''
            db=self.data[version]
            if function!=None:
                con={"t_hash":md5(function)}
            else:con=None
            ret={}
            for r in db.group(["date","t_hash"],con,{"count":0,"t":""},func):
                ret[r['date']]=int(r['count'])
            #ret=self.db.find({"t_hash":md5(function)})
            return ret
        except Exception as e:
            print e
            pass
        return []
    def getTrac(self,version):
        try:
            func = '''
                function(obj, prev)
                {
                    if(prev.count==0)
                    {
                        prev.o=obj;
                        prev.t=obj.t;
                    }
                    prev.count++;
                }
               '''
            db=self.data[version]
            result=db.group(["t_hash"],None,{"count":0,"t":"","o":""},func)
            result = sorted(result, key = lambda x:x['count'], reverse = True)
        #<td width="50px"  align="center" bgcolor="#FFFFFF" >{{ t.count|e }}</td>
        #<td width="50px"  align="center"bgcolor="#FFFFFF">{{ t.date|e }}</td>
        #<td width="50px"  align="left"bgcolor="#FFFFFF">{{ t.reason|e }}</td>
        #<td width="50px"  align="left"bgcolor="#FFFFFF"><a href="func/{{ t.trac|e }}">{{ t.trac|e }} </a> </td>
        #<td width="50px"  align="left"bgcolor="#FFFFFF">
        # [<a href="did/{{ t.trac|e }}">device</a>]
        # [<a href="/lb/{{version}}/func/{{ t.trac|e }}/log">log</a>]
        # [<a href="/lb/same/func/{{ t.trac|e }}">same</a>]
        # [<a href="/lb/{{version}}/dailyfunccount/{{ t.trac|e }}">daily</a>]
            ret=[]
            for r in result:
                l=r['o']
                ret.append({"count":int(r['count']),"trac":r['t'],"reason":l['reason'],"date":l['date']})
            #ret=self.db.find({"t_hash":md5(function)})
            return ret
        except Exception as e:
            print e
            pass
        return []
    def group(self,tag="b",sort=True,version='1.7.8777.406',date=None):
        from bson.code import Code
        mapfun = Code("function () {emit(this.%s, 1)};"%(tag))
        reducefun = Code("function (key, values) {"
                       "  var total = 0;"
                       "  for (var i = 0; i < values.length; i++) {"
                       "    total += values[i];"
                       "  }"
                       "  return total;"
                       "}")
        result = self.data[version].map_reduce(mapfun, reducefun, "myresults").find()
        result = sorted(result, key = lambda x:x['value'], reverse = True)
        return result



db=db_crashlog()
def save(c):
    key=crashkey(c)
    if key.module_crashat():
        db.connect()
        db.save(key,c)
        pass
    return

def test():
    #import crash
    #c=crash.crash(t)
    #crashkey(c).module_crashat()
    pass
#test()

def updatedailyCrashCount(version):
    pass


def updateTodayCrashCount(version):
    pass

if __name__ == "__main__":
    def longest_common_substring(s1, s2):
        m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
        longest, x_longest = 0, 0
        for x in xrange(1, 1 + len(s1)):
            for y in xrange(1, 1 + len(s2)):
                if s1[x - 1] == s2[y - 1]:
                    m[x][y] = m[x - 1][y - 1] + 1
                    if m[x][y] > longest:
                        longest = m[x][y]
                        x_longest = x
                else:
                    m[x][y] = 0
        return s1[x_longest - longest: x_longest]
    versionlist=["2.3.10285.642"]
    db.connect().getTrac('2.1.9762.532')
    #import main
    #try:
    #    def enableindex(versionlist):
    #        try:
    #            db_crashlog().connect().EnableIndexWithField(versionlist,"id")
    #            db_crashlog().connect().EnableIndexWithField(versionlist,"t")
    #            db_crashlog().connect().EnableIndexWithField(versionlist,[("t", pymongo.ASCENDING),("date", pymongo.ASCENDING)])
    #        except:pass
    #    enableindex(["1.6.8303.380","1.5.6881.318"])
    #except:
    #    pass

    #longest_common_substring(["1","1234","a"],["2","1234","b"])
    #db_crashlog().connect().updatealltrac("1.8.8856.414")
    #db_crashlog().connect().updatealltrac("1.7.8777.406")
    #db_crashlog().connect().updatealltrac("1.8.9055.443")
    #db_crashlog().connect().updatealltrac("1.8.8860.418")
    #db_crashlog().connect().getdailyFunctionCrashWithVersion()
    #db_crashlog().connect().findNone(version="1.8.8856.414")
    #db_crashlog().connect().getlog()
    #db_crashlog().connect().dailytopcrash("20140328","2.0.9429.483")
    #db_crashlog().connect().EnableIndexWithField(["2.0.9429.483","2.1.9707.521"],"id")
    #db_crashlog().connect().EnableIndexWithField(["2.0.9429.483","2.1.9707.521"],"t")
    #db_crashlog().connect().checknewTrac("2.0.9429.483")
    #db_crashlog().connect().checknewTrac("2.1.9707.521")
    #db_crashlog().connect().findFuncitonWithContion(enabledid=True,version="2.0.9429.483",condtion={"t":"-[LBHomePageViewController initWithNibName:bundle:]"})




