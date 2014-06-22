import sys
import os
import ConfigParser
import objgraph
import inspect
from  profile import *

__author__ = 'doskey'
import objgraph

DEBUG = True
CONFIG_FILE = 'config.ini'

global_config = None
import  crash
import  crashdb
root=os.path.abspath(os.path.join(os.getcwd(),os.path.pardir))
def read_config(path):
    global  CONFIG_FILE
    config_path = os.path.join(path, CONFIG_FILE)
    if not os.path.exists(config_path):
        print 'Cannot find config.ini in current path.'
        sys.exit(-1)

    conf = ConfigParser.ConfigParser()
    try:
        conf.read(os.path.join(path, CONFIG_FILE))
    except:
        print 'Failed to open config.ini.'
        sys.exit(-1)

    return conf


def download_files(date):
    import  download
    return download.wget(date)


def generate_date_list():
    import datetime
    def today():
        import datetime
        return datetime.datetime.now()
    date_format = global_config.get('Settings', 'DateFormat')
    def getdate(date):

        try:
            end_date=global_config.get('Settings',date, date_format)
            end_date = datetime.datetime.strptime(end_date, date_format)
        except:
            end_date=today()
        return end_date

    start_date=getdate("StartDate")
    end_date = getdate('EndDate')
    r = end_date - start_date
    one_day = datetime.timedelta(days = 1)
    days = []

    if r.days == 0:
        days.append(start_date.strftime(date_format))
    elif r.days > 0:
        for i in range(0, r.days+1):
            days.append(start_date.strftime(date_format))
            start_date = start_date + one_day
    elif r.days < 0:
        print 'ERROR: EndDate is eariler than StartDate.'
        sys.exit(-1)

    return days


def create_temp_direcotry():
    temp_path = os.path.expanduser(global_config.get('Settings', 'TempPath'))
    if os.path.exists(temp_path):
        import shutil
        shutil.rmtree(temp_path)

    os.mkdir(temp_path)
    return temp_path

def data_transfer():
    pass

def analyze_call_stack(symbloics,verson):
    import os
    archive=os.path.abspath(os.path.join(root,'archive'))
    binary_path = archive+'/%s/ksmobilebrowser.app/ksmobilebrowser'%(verson)
    #xcrun -find -sdk iphoneos atos


    import subprocess
    cmd = [
        '/Applications/Xcode.app/Contents/Developer/usr/bin/atos',
        '-d',
        '-o', binary_path,
        '-arch', 'armv7',
        '-l', '0x%x' % 0x1000
    ]
    cmd = [
        '/usr/bin/atos',
        '-d',
        '-o', binary_path,
        '-arch', 'armv7',
        '-l', '0x%x' % 0x1000
    ]

    for sym in symbloics:
        cmd.append('0x%x' % sym['address'])

    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    i = 0
    for line in output.split('\n'):
        if len(line) == 0:
            continue
        symbloics[i]['symbolic'] = line.replace(' (in ksmobilebrowser)', '').rstrip()
        i += 1
    return symbloics

class lib(object):
        def __init__(self,line):
            self.name="1"
            return;
def data_analyze(file_path, core_module,symbolics):
    address_delta = int()
    crush_data = dict(
        version = str(),
        reason = str(),
        count = int(),
        device_info = dict(
            jb = int(),
            nojb = int(),
            device = dict(),
            os = dict()
        ),
        library=dict(),
        base_address = int(),
        call_stack = list(),
        path=str()
    )


    with open(file_path, 'r') as f:
        is_call_stack = False
        crush_data['path']=file_path
        for lines in f:
            lines = lines.strip()
            def v2():
                taglib="- ???"
                if lines.find(taglib)!=-1:
                    l=lib(lines)
                    crush_data[l.name]=l
                    return True
                return False



            def v1(is_call_stack):
                key=None
                value=None
                if not is_call_stack:
                    key_value = lines.split(':')
                    if len(key_value) > 1:
                        key = key_value[0]
                        value = key_value[1]
                    else:
                        is_call_stack = True
                return (is_call_stack,key,value)
            if v2():
                continue
            vv1=v1(is_call_stack)
            is_call_stack=vv1[0]
            key=vv1[1]
            value=vv1[2]
            if is_call_stack:
                stack = dict(
                    id = int(lines[0:4].rstrip(' ')),
                    module = lines[4:40].rstrip(' '),
                    address = int(lines[40:50].rstrip(''), 16),
                    symbolic = lines[51:].rstrip(' ')
                )

                if stack['module'] == core_module:
                    stack['address'] -= address_delta

                    is_exist = False
                    for sym in symbolics:
                        if stack['address'] == sym['address']:
                            is_exist = True
                            break

                    if not is_exist:
                        sym = dict(
                            address = stack['address'],
                            symbolic = str()
                        )

                        symbolics.append(sym)
                crush_data['call_stack'].append(stack)

            elif key == 'appver':
                crush_data['version'] = value
            elif key == 'did':
                crush_data['did'] = value
            elif key == 'baseaddr':
                #crush_data['base_address'] = value
                crush_data['base_address'] = 0x1000
                address_delta = int(value, 16) - 0x1000

            elif key == 'device':
                device_info = value.split('|')

                if device_info[0] in crush_data['device_info']['device']:
                    crush_data['device_info']['device'][device_info[0]] += 1
                else:
                    crush_data['device_info']['device'][device_info[0]] = 1

                if device_info[1] in crush_data['device_info']['os']:
                    crush_data['device_info']['os']=device_info[1]
                else:
                    crush_data['device_info']['os']=device_info[1]

                if device_info[2] == '0':
                    crush_data['device_info']['nojb'] += 1
                elif device_info[2] == '1':
                    crush_data['device_info']['jb'] += 1

            elif key == 'info':
                crush_data['reason'] = lines.split('info:')[1]

    crush_data['count'] = crush_data['device_info']['nojb'] + crush_data['device_info']['jb']
    return crush_data




global versionlist
#versionlist=["1.8.8856.414",
#              "1.7.8777.406",
#              "1.8.9055.443","1.8.8860.418","1.9.9287.455","2.0.9429.483","2.1.9707.521","2.1.9762.532","2.1.9762.534","2.3.10118.619","2.3.10285.642"]
versionlist=None
def getdatelistFromConfig():
    global global_config
    import os
    hi(lineno())
    try:
        days = generate_date_list()
    except:
        import datetime
        y=datetime.datetime.now().date().year
        m=datetime.datetime.now().date().month
        d=datetime.datetime.now().date().day
        now ="%d%02d%02d"%(y,m,d)
        days=[now]
    return days
def main():
    #diddownload()
    global versionlist
    for v in versionlist:
        for day in getdatelistFromConfig():
            didmain(day,v,True)
        #crashdb.db_crashlog().connect().updatedailycrashWithVersion(version=v)

def diddownload(current_path=os.getcwd(),download=True):
    try:
        days = generate_date_list()
    except:
        import datetime
        y=datetime.datetime.now().date().year
        m=datetime.datetime.now().date().month
        d=datetime.datetime.now().date().day
        now ="%d%02d%02d"%(y,m,d)
        days=[now]

    def downloadfile(d):
        downloaded=False
        if d==False:
            return
        for d in days:
            print "Begin download %s"%(d)
            if download_files(d)==True:
                downloaded=True
        if downloaded==False:
            print "No file"
        return downloaded
    downloaded=downloadfile(download)

def didmain_old(version="",download=True):
    global global_config
    import os
    current_path = os.getcwd()
    #    return
    #temp_path = prepare_temp_direcotry()
    temp_path=os.path.join(root,"log/")

    core_module = global_config.get('App', 'CoreModule').lower()
    symbolic_black_list = global_config.get('App', 'SymbolicBlackList').split(',')
    s=1
    hi(lineno())
    try:
        days = generate_date_list()
    except:
        import datetime
        y=datetime.datetime.now().date().year
        m=datetime.datetime.now().date().month
        d=datetime.datetime.now().date().day
        now ="%d%02d%02d"%(y,m,d)
        days=[now]

    for day in days:
        fileflag=day+".done"
        if os.path.exists(fileflag):continue
        download_files(day)
        db = list()
        total_data = int()
        symbolics = list()
        data_path = os.path.join(temp_path, day)
        try:
            file_name_list = os.listdir(data_path)
        except:
            continue

        print 'Processing ' + day + '...'
        hi(lineno())
        for file_name in file_name_list:
            log2=os.path.abspath(os.path.join(root,'logjson'))
            log2=os.path.abspath(os.path.join(log2,day))
            log2=os.path.abspath(os.path.join(log2,file_name+".json"))
            if os.path.exists(log2):continue
            if not file_name.startswith(version):
                continue
            try:
                if crashdb.db.connect().findByID(version=version,ID=file_name)==True:
                    continue
            except Exception as e:
                pass
            total_data += 1
            try:
                data = data_analyze(os.path.join(data_path, file_name), core_module,symbolics)
            except Exception as e:
                data = None
            if data != None:
                data['date']=day
                db.append(data)
        hi(lineno())
        if len(symbolics):
            analyze_call_stack(symbolics,version)
        hi(lineno())
        for data in db:
            for stack in data['call_stack']:
                if stack['module'] == core_module:
                    for sym in symbolics:
                        if sym['address'] == stack['address']:
                            stack['symbolic'] = sym['symbolic']
                            break
        hi(lineno())
        for data in db:
            hi(lineno())
            c=crash.crash(data)
            hi(lineno())
            crashdb.save(c)
            import os
            log2=os.path.abspath(os.path.join(root,'logjson'))
            try:os.mkdir(log2)
            except:pass

            log2=os.path.abspath(os.path.join(log2,day))
            try:os.mkdir(log2)
            except:pass
            c.save(log2)
            del c
            hi(lineno())
        open(fileflag,"w").write("done")

def didmain(day=None,version="",download=True):
    if download:
        download=download_files(date=day)
    else:
        download=True
    fileflag="____%s %s"%(day,version)
    import os
    if os.path.exists(fileflag) and download==False:return
    def cb(c):
        crashdb.save(c)
    if download:
        pareseLogAtDay(day,version,cb=None)
    open(fileflag,"w").write("done")

def pareseLogAtDay(day,version,cb):
    temp_path=os.path.join(root,"log/")
    core_module = global_config.get('App', 'CoreModule').lower()
    symbolic_black_list = global_config.get('App', 'SymbolicBlackList').split(',')
    s=1
    def processlogatday(day,version,cb=None):
        import os
        db = list()
        total_data = int()
        symbolics = list()
        data_path = os.path.join(temp_path, day)
        try:
            file_name_list = os.listdir(data_path)
        except:
            return None

        print 'Processing ' + day + '...'
        hi(lineno())
        for file_name in file_name_list:
            log2=os.path.abspath(os.path.join(root,'logjson'))
            log2=os.path.abspath(os.path.join(log2,day))
            log2=os.path.abspath(os.path.join(log2,file_name+".json"))
            if os.path.exists(log2):continue
            if not file_name.startswith(version):
                continue
            try:
                if crashdb.db.connect().findByID(version=version,ID=file_name)==True:
                    continue
            except Exception as e:
                pass
            total_data += 1
            try:
                data = data_analyze(os.path.join(data_path, file_name), core_module,symbolics)
            except Exception as e:
                data = None
            if data != None:
                data['date']=day
                db.append(data)
        hi(lineno())
        if len(symbolics):
            analyze_call_stack(symbolics,version)
        hi(lineno())
        for data in db:
            for stack in data['call_stack']:
                if stack['module'] == core_module:
                    for sym in symbolics:
                        if sym['address'] == stack['address']:
                            stack['symbolic'] = sym['symbolic']
                            break
        hi(lineno())
        for data in db:
            hi(lineno())
            c=crash.crash(data)
            hi(lineno())
            if cb!=None:
                cb(c)
            import os
            log2=os.path.abspath(os.path.join(root,'logjson'))
            try:os.mkdir(log2)
            except:pass

            log2=os.path.abspath(os.path.join(log2,day))
            try:os.mkdir(log2)
            except:pass
            c.save(log2)
            del c
            hi(lineno())
    return processlogatday(day,version)
import gc
if __name__ == "__main__":
    #
    print 'begin collect...'
    import  sys
    print sys.argv
    global CONFIG_FILE
    CONFIG_FILE=sys.argv[1]

    global versionlist
    global global_config
    global_config = read_config(os.getcwd())

    versionlist=global_config.get('Settings', 'Version')
    versionlist=versionlist.split(',')
    #print gc.get_objects()
    #gc.enable()
    #gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
    #print gc.set_debug(gc.DEBUG_LEAK)
    print '----------->'
    import  crashdb
    main()
    #import  crashdb
    #for v in versionlist:
    #    crashdb.db_crashlog().connect().updatealltrac(v)
    #    crashdb.db_crashlog().connect().checknewTrac(v)
    #    crashdb.db_crashlog().connect().updatedailycrashWithVersion(v)
    #    crashdb.updateTodayCrashCount(v)
    #_unreachable = gc.collect()
    #print 'unreachable object num:%d' % _unreachable
    #print 'garbage object num:%d' % len(gc.garbage)
    
