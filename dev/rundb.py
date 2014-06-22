__author__ = 'acb'
import  crashdb
if __name__ == "__main__":
    import sys
    import  hashlib
    s=hashlib.md5("1").hexdigest()
    #crashdb.updatedailyCrashCount(sys.argv[1])
    version="1.6.8303.380"
    version=sys.argv[1]
    versions=sys.argv[1:]
    print versions
    for version in versions:
        crashdb.updatedailyCrashCount(version)
        crashdb.db_crashlog().connect().EnableIndexWithField(version)
        db=crashdb.db_crashlog().connect()
        db.trac.EnableIndexWithField(version)
        #db.tracdaily.EnableIndexWithField(version)
