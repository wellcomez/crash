from sql import *
version="2.2.10460.667"
def test1():
    v=["1.5.6881.318","1.6.8303.380","1.8.8856.414","2.0.9429.483","2.1.9762.532","2.2.10460.667"]
    for version in v:
        c=DailyCrash(sql.instance().conn,version)
        c.updateall()

def test2():
    v=["1.5.6881.318","1.6.8303.380","1.8.8856.414","2.0.9429.483","2.1.9762.532","2.2.10460.667"]
    for version in v:
        try:
            l=logdata(sql.instance().conn,version)
            l.updateall()
        except:
            pass

test2()