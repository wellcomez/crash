__author__ = 'acb'
import os
def  now():
    import datetime
    s=datetime.datetime.now()
    s=s.strftime("%Y_%m_%d[%H:%M:%S]")
    return s

root=os.path.abspath(os.path.join(os.getcwd(),os.path.pardir))
log=os.path.join(root,"log")
logjson=os.path.join(root,"logjson")
fin=os.path.join(root,"fin")
tmp=os.path.join(root,"tmp")

class globalconfig(object):
    def __init__(self,file='config.ini'):
        self.CONFIG_FILE =file
        self.root=os.path.abspath(os.path.join(os.getcwd(),os.path.pardir))
        self.global_config = self.__read_config(self.root)
        self.symbolic_black_list = self.global_config.get('App', 'SymbolicBlackList').split(',')
        self.versionlist=self.global_config.get('Settings', 'Version').split(',')
        self.moudle=self.global_config.get('App', 'CoreModule').lower()
        self.archive=os.path.join(self.root,"archive/")
        self.log=os.path.join(self.root,"log")
        self.logjson=os.path.join(self.root,"logjson")
        self.fin=os.path.join(self.root,"fin")
        self.tmp=os.path.join(self.root,"tmp")
    def __read_config(self,dir):
        config_path = os.path.join(dir, self.CONFIG_FILE)
        if not os.path.exists(config_path):
            raise 'Cannot find config.ini in current path.'
        import ConfigParser
        conf = ConfigParser.ConfigParser()
        try:
            conf.read(os.path.join(dir, self.CONFIG_FILE))
        except:
            raise 'Failed to open config.ini.'
        return conf
    def generate_date_list(self):
        import datetime
        def today():
            import datetime
            return datetime.datetime.now()
        date_format = self.global_config.get('Settings', 'DateFormat')
        def getdate(date):

            try:
                end_date=self.global_config.get('Settings',date, date_format)
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
            raise 'ERROR: EndDate is eariler than StartDate.'
        return days

    def dir_create_temp_direcotry(self):
        temp_path = os.path.expanduser(self.global_config.get('Settings', 'TempPath'))
        if os.path.exists(temp_path):
            import shutil
            shutil.rmtree(temp_path)
        os.mkdir(temp_path)
        return temp_path
    def mklogjsondaydir(self,day=None):
        try:
            os.mkdir(os.path.join(self.logjson,day))
        except:
            pass
        return os.path.join(self.logjson,day)
    def file_logjson(self,day=None,filename=None):
        log2=self.logjson
        if day==None:
            return log2
        log2=os.path.abspath(os.path.join(log2,day))
        if filename==None:
            return log2;
        log2=os.path.abspath(os.path.join(log2,filename+".json"))
        return log2
    def file_symbolbin(self,version,app='ksmobilebrowser'):
        binary_path = self.archive+'/%s/%s.app/%s'%(version,app,app)
        return binary_path
    def file_fin(self,version,date):
        r=self.fin;
        return os.path.abspath(os.path.join(r,version+date))

if __name__ == "__main__":
    ccc=globalconfig("dev/config.ini.test")
    print ccc.generate_date_list()
    print ccc.archive
    print ccc.log
    print ccc.file_symbolbin("1.0")
    print(ccc.fin)
    print(ccc.file_fin("1.0","2014"))
    print(ccc.file_logjson("2014","aaaa"))
    pass
