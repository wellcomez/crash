from crash import *
from keydb import *
from sql   import *
class crashsys(object):
    def __init__(self):
        self.db=keydb("crashsys").connect()
        pass
    def find(self,chash):
        return self.db.find(chash)
    def save(self,t,c):
        self.db.save(t,c)

def find(version):
    import table_groupbycallstack
    import crashlog
    db=table_groupbycallstack.table_groupbycallstack(version,sql.instance().conn())
    result=db.find_log_with_samefunciton("")
    for r in result:
        fn=r['id']
        c=crashlog.crashlog().rawlogid(fn)
        key=crashkey(c)
        key.findlongestchain()
        if key.crashtop!=None and len(key.crashtop)>0:
            r['t_hash']=key.crashtop
