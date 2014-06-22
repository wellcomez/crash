__author__ = 'zhujialai'
#download_files(os.getcwd())
def wget(date):
    import  os
    cwd=os.getcwd()
    ssss=os.path.abspath(os.path.join(os.getcwd(),os.path.pardir))
    logdir=os.path.abspath(os.path.join(ssss,'log'))
    codedir=os.path.abspath(os.path.join(ssss,'code'))
    shpath=os.path.abspath(os.path.join(codedir,'download.sh'))
    os.chdir(logdir)

    cmd=["/bin/bash",shpath,date]
    import subprocess

    def getdownload():
        downloaded=0
        try:
            downloaded=len(os.listdir(os.path.join(logdir,date)))
        except Exception as e:
            pass
        return downloaded

    d1=getdownload()
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    os.chdir(cwd)
    d2=getdownload()

    print "d1 %d d2 %d %d"%(d1,d2,d2-d1)
    return d2-d1>0

def __download_files(date):
    import  download
    return download.wget(date)

def down(d):
    print "Begin download %s"%(d)
    downloaded=False
    if __download_files(d)==True:
        downloaded=True
    if downloaded==False:
        print "No file"
    return downloaded

if __name__ == "__main__":
    import globalconfig
    import os
    import sys
    try:
        dir=sys.argv[1]
    except:
        dir="config.ini.1.6.8303.380"
    ccc=globalconfig.globalconfig(os.path.join(os.getcwd(),dir))
    for day in ccc.generate_date_list():
        down(day)
    #wget('20140301')