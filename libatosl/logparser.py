__author__ = 'acb'
from  profile import *
import  globalconfig
class lib(object):
    def __init__(self,line):
        self.name="1"
        return;

class logparser(object):
    def __init__(self,c,version):
        self.c=c
        self.version=version
        self.app=self.c.file_symbolbin(version)
        self.log=self.c.log
        self.core_module=self.c.moudle
        self.symbolic_black_list =c.symbolic_black_list

    def data_analyze(self,file_path, core_module,symbolics):
        print file_path
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

    def analyze_call_stack(self,symbloics,verson):
        #print symbloics
        import os
        binary_path = self.app
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

    def pareseLogAtDay(self,day,cb,cb_prev=None):
        objects=[]
        core_module =self.core_module
        symbolic_black_list = self.symbolic_black_list
        s=1
        def processlogatday(day,version,cb=None,cb_prev=None):
            import os
            db = list()
            total_data = int()
            symbolics = list()
            data_path = os.path.join(self.log, day)
            try:
                file_name_list = os.listdir(data_path)
            except:
                return None

            print 'Processing ' + day + '...'
            hi(lineno())
            symbolics2={}
            for file_name in file_name_list:
                log2=self.c.file_logjson(day,file_name)
                if os.path.exists(log2):continue
                if not file_name.startswith(version):
                    continue
                total_data += 1
                try:
                    data = self.data_analyze(os.path.join(data_path, file_name), core_module,symbolics)
                except Exception as e:
                    data = None
                if data != None:
                    data['date']=day
                    db.append(data)
                if len(symbolics)>100:
                    #print  symbolics
                    symbolics_ret=self.analyze_call_stack(symbolics,version)
                    for s in symbolics_ret:
                        symbolics2[s['address']]=s['symbolic']
                    symbolics=list()


            if len(symbolics):
                symbolics_ret=self.analyze_call_stack(symbolics,version)
                for s in symbolics_ret:
                    symbolics2[s['address']]=s['symbolic']


            for data in db:
                for stack in data['call_stack']:
                    if stack['module'] == core_module:
                        try:
                            symbol=symbolics2[stack['address']]
                            stack['symbolic'] = symbol;
                            #print data
                        except Exception as e:
                            print e
            hi(lineno())
            print "create crashlog"
            for data in db:
                hi(lineno())
                import crash
                #print 1,data
                c=crash.crash(data)
                #print 2
                hi(lineno())
                #print 3
                dir=self.c.mklogjsondaydir(day)
                #print c.id
                f=c.save(dir)
                if cb!=None:
                    cb(c,f)
                del c
                hi(lineno())
            return len(db)

        return processlogatday(day,self.version,cb)

logs=[]
import globalconfig
def newcrashfile():
    s=globalconfig.tmp
    path=os.path.join(globalconfig.tmp,"newcrash_%s.json"%(s))
    return path
if __name__ == "__main__":

    import os
    import sys
    try:
        dir=sys.argv[1]
    except:
        dir="config.ini.2.2.10460.667"
    c=globalconfig.globalconfig(os.path.join(os.getcwd(),dir))
    for version in c.versionlist:
        p=logparser(c,version)
        for day in c.generate_date_list():
            def cb(c,f):
                import crashdb
                global logs
                key=crashdb.crashkey(c)
                if key.module_crashat():
                    logs.append(f)
                    pass
            p.pareseLogAtDay(day,cb)
    print logs
    import json
    json.dump(logs,open(newcrashfile(),"wb"));
