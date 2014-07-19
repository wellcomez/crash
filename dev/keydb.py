from pyelevator import Elevator
class keydb(object):
    def __init__(self,name):
	self.name=name
	self.ce=None
    def connect(self):
	if self.ce!=None :return self
	self.synced=False
	self.ce=Elevator()
	try:
	    self.ce.connect(self.name)
	except Exception as e:
	    self.ce.createdb(name)
	    self.ce.connect(self.name)
	return self
    def find(self,key):
        v=self.ce.Get(key)
        if v==None:return None
	import json
	v=json.loads(v)
	return v
    def save(self,k,v):
        import json
        v=json.dumps(v)
        self.ce.Put(k,v)
        return True
    def has(self,k):
	return self.find(k)!=None
    def close(self):
        if self.synced==False:
            self.ce.WriteBatch()
        self.synced=True
    def __del__(self):
        self.close()


