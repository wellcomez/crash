__author__ = 'zhujialai'
import web

### Url mappings
class URLRE:
    VERSION="(\d[.\d]+\d)"
    def __init__(self):
        return
urls = (
    "/search?(.*)$",'search',
    "/",'index',
    '/json/lb/', 'lb',
    '/lb$', 'index',
    #>>> print re.compile("\d{1,4}").findall("1.2893.3")
    '/lb/'+URLRE.VERSION+'$', 'lbversion',
    #'/json/lb/(/d\./d)',    'appversion',
    "/lb/%s/[tb](/d+)"%(URLRE.VERSION),    "crashlist",
    "/lb/%s/func/(.*)$"%(URLRE.VERSION),  "crash",
    "/lb/%s/dailyfunccount/(.*)$"%(URLRE.VERSION),  "crashdailyCount",
    "/lb/%s/did/(.*)$"%(URLRE.VERSION),  "samedid",
    "/lb/%s/log/(.*)$"%(URLRE.VERSION),  "crashlog",
    "/lb/%s/trac$"%(URLRE.VERSION),  "trac",
    "/lb/%s/day$"%(URLRE.VERSION),  "day",
    "/lb/same/func/(.*)$",  "samecrash",
    "/lb/%s/day/func/(.*)$"%(URLRE.VERSION),  "dayfunc",
    "/lb/%s/day/update$"%(URLRE.VERSION),  "dayupdate"
    #"/lb/%s/day/(/d+)$"%(URLRE.VERSION),  "day"

)
from web.contrib.template import render_jinja
render = render_jinja(
    'templates',
    encoding = 'utf-8',
)
#import  crashdb
import sql
class lbversion:
    def GET(self,v):
        #a='''<a href="%s/trac">'''%(v)+"trac"+'''<a/><br>'''+'''<a href="%s/day">'''%(v)+"day"+'''<a/><br>'''
        import datetime
        day=datetime.datetime.now()
        date="%d%02d%02d"%(day.year,day.month,day.day)
        result=crashdb.db.dailytopcrash(date=date,version=v)
        html=[]
        for i in result:
            html.append({"name":i['data']['t'],"count":i['count']})
        return render.crashversion(version=v,crash=html)#(crash=html,version=v)
class search:
    def GET(self,query):
        return query
class lb:
    def GET(self):
        return "1111"
class trac:
    def GET(self,version):
        try:
            query=sql.sql.instance()
            r=query.groupTrac(version)
        except Exception as e:
            print e
        return render.trac(trac=r,version=version)

class dayupdate:
    def GET(self,version):
        import json
        result=sql.sql.connect().setdailycrashWithVersion(version)
        return render.date(value=json.dumps(result),title=version)
class day:
    def GET(self,version):
        ret=sql.sql.connect().getdailycrashWithVersion(version)
        import  json
        return render.date(value=json.dumps(ret),title=version)
class dayfunc:
    def GET(self,version):
        return ""
        #ret=crashdb.db_crashlog().connect().getdailycrashWithVersion(version)
        #return render.date(value=ret,title=version)


class index:
    def GET(self):
        return render.lb(versions=sql.sql.connect().collection_names(),dates=["1","2"])

#"/lb/%s/func/(.*)$"%(URLRE.VERSION),  "crash",
class crashdailyCount:
    def GET(self,version,trac):

        #import crashdb
        import json
        #ret=crashdb.db.connect().getDailyCrash(version,trac)
        ret=sql.sql.connect().getDailyCrash(version,trac)
        return render.date(value=json.dumps(ret),title=trac)
class crashlog:
    def GET(self,version,id):
        log=sql.log(conn=sql.sql.instance().conn,version=version).readlogfile(id,version)
        return log;
        import jsonpickle
        frames=jsonpickle.decode(log['stack'])
        stack=[]
        for f in frames:
            tb='''<tr >
    <td width="150px"  align="left" bgcolor="#FFFFFF" >0x%08x</td>
    <td width="400px"  align="left" bgcolor="#FFFFFF">%s</td>
    <td align="left" style="word-wrap:break-word;" bgcolor="#FFFFFF">%s</td>
</tr>'''%(f['a'],f['m'], f['f'])
            stack.append(tb)
        stacklog=[]
        stacklog.append({"stack":stack,"reason":log["reason"],"device":""})
        ret=render.log(stacks=stacklog,log=log['id'])
        return ret
    def GETNOSQL(self,version,id):
        import crashdb
        result=crashdb.db.connect().findLog(id=id,version=version)
        import  jsonpickle
        log=jsonpickle.decode(result['log'])
        stacklog=[]
        stack=[]
        for f in log.stack.frames:
            tb='''<tr ><td width="150px"  align="left" bgcolor="#FFFFFF" >0x%08x</td><td width="400px"  align="left" bgcolor="#FFFFFF">%s</td><td align="left" style="word-wrap:break-word;" bgcolor="#FFFFFF">%s</td></tr>'''%(f.address,f.function.module, f.symblic)
            stack.append(tb)

        ret2=result['device']
        ret2=jsonpickle.encode(ret2)

        import os
        f=os.path.abspath(os.path.join(os.getcwd(),os.path.pardir))
        for p in ["log",log.dir,log.id]:
            f=os.path.join(f,p)
        s=[]
        for i in open(f).readlines():
            s.append(i)
            s.append("<br>")
        stacklog.append({"stack":stack,"reason":log.reason,"count":len(stack),"device":ret2,"data":"".join(s)})
        ret=render.log(stacks=stacklog,log=log.id)
        return ret

class samecrash:
    def GET(self,func):
        return render.sametrac(trac=sql.sql.connect().findFuncitonCount(function=func),function=func)
class samedid:
    def GET(self,version,func):
        import crashdb
        all=sql.sql.connect().findFuncitonWithSameDid(version=version,function=func)
        return  render.userlist(version=version,list=all,function=func)
class crash:
    def GET2(self,version,func):
        #import crashdb
        import jsonpickle
        l=sql.log(version=version,conn=sql.sql.instance().conn)
        ret=l.findFunciton(function=func,version=version,unique=False)
        stacklog=[]
        for r in ret:
            stacklog.append({"version":version,"logid":r['id'],"os":r['os']})
        return render.loglist(log=stacklog,function=func)

    def GETLogDetail(self,version,func):
        try:
            l=sql.log(version=version,conn=sql.sql.instance().conn)
            ret=l.findFunciton(function=func,version=version,unique=True)
        except Exception as e:
            pass
        stacklog=[]
        for r in ret:
            stacklog.append({"version":version,"logid":r['id'],"os":r['os']})
        return render.loglist(log=stacklog,function=func)

        stacklog=[]
        import jsonpickle
        for i in range(0,len(ret)):
            log=ret[i]
            count=log['count']
            frames=log['stack']
            frames=jsonpickle.decode(frames)
            #log=jsonpickle.decode(ret[i]["data"]["log"])
            #count=ret[i]["count"]
            stack=[]
            i=0
            crashIndex=0
            for f in frames:
                tb='''<tr >
        <td width="150px"  align="left" bgcolor="#FFFFFF" >0x%08x</td>
        <td width="400px"  align="left" bgcolor="#FFFFFF">%s</td>
        <td align="left" style="word-wrap:break-word;" bgcolor="#FFFFFF">%s</td>
    </tr>'''%(f['a'],f['m'], f['f'])
                stack.append(tb)
                try:
                    if f['f']==func:
                        crashIndex=i
                except Exception as e:
                    #print e
                    pass
                i=i+1

            stacklog.append({"stack":stack,"reason":log['reason'],"count":count,"index":crashIndex})
        ret=render.detail(stacks=stacklog,func=func)
        return ret
    def GET(self,version,func):
        log=func[len(func)-3:len(func)]
        if log=="log":
            return self.GET2(version,func[0:len(func)-4])
        return self.GETLogDetail(version,func)
        import crashdb
        import jsonpickle
        ret=crashdb.db.connect().findLogFileWithFunction(function=func,version=version)
        stacklog=[]
        for i in range(0,len(ret)):
            log=ret[i]
            count=log['count']
            frames=log['frame']
            frames=jsonpickle.decode(frames)
            #log=jsonpickle.decode(ret[i]["data"]["log"])
            #count=ret[i]["count"]
            stack=[]
            i=0
            crashIndex=0
            for f in frames:
                tb='''<tr >
        <td width="150px"  align="left" bgcolor="#FFFFFF" >0x%08x</td>
        <td width="400px"  align="left" bgcolor="#FFFFFF">%s</td>
        <td align="left" style="word-wrap:break-word;" bgcolor="#FFFFFF">%s</td>
    </tr>'''%(f['a'],f['m'], f['f'])
                stack.append(tb)
                try:
                    if f['f']==func:
                        crashIndex=i
                except Exception as e:
                    #print e
                    pass
                i=i+1

            stacklog.append({"stack":stack,"reason":log['reason'],"count":count,"index":crashIndex})
        ret=render.detail(stacks=stacklog,func=func)
        return ret
class crashlist:
    def GET(self,version,n):
        import crashdb
        top=int(n)
        import  crashdb
        result=crashdb.db.group(tag="t",version=version)
        return render.lbresult(results=result,version=version)
class appversion:
    def GET(self,app,version):
        return

class productlist:
    def GET(self,name):
        return ""
app = web.application(urls, globals())
if __name__ == '__main__':
    app.run()
