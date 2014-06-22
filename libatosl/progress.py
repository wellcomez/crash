#!/usr/bin/env python
# -*- coding=utf-8 -*-
#Using GPL v2
#Author: ihipop@gmail.com
#2010-10-30 13:59
"""
Usage:
Just A Template
"""
class progressbarClass:
    def __init__(self, finalcount, progresschar=None):
        import sys
        self.finalcount=finalcount
        self.blockcount=0
        #
        # See if caller passed me a character to use on the
        # progress bar (like "*").  If not use the block
        # character that makes it look like a real progress
        # bar.
        #
        if not progresschar: self.block=chr(178)
        else:                self.block=progresschar
        #
        # Get pointer to sys.stdout so I can use the write/flush
        # methods to display the progress bar.
        #
        self.f=sys.stdout
        #
        # If the final count is zero, don't start the progress gauge
        #
        if not self.finalcount : return
        self.f.write('\n------------------- % Progress -------------------\n')
        return

    def progress(self, count):
        #
        # Make sure I don't try to go off the end (e.g. >100%)
        #
        count=min(count, self.finalcount)
        #
        # If finalcount is zero, I'm done
        #
        if self.finalcount:
            percentcomplete=int(round(100*count/self.finalcount))
            if percentcomplete < 1: percentcomplete=1
        else:
            percentcomplete=100

        #print "percentcomplete=",percentcomplete
        blockcount=int(percentcomplete/2)
        #print "blockcount=",blockcount
        if blockcount > self.blockcount:
            for i in range(self.blockcount,blockcount):
                self.f.write(self.block)
                self.f.flush()

        if percentcomplete == 100: self.f.write("\n")
        self.blockcount=blockcount
        return
import time
class tc(object):
    def __init__(self):
        self.begin=time.time()
    def end(self):
        c=time.time()-self.begin
        print  c
        self.begin=time.time()
        return c
if __name__ == "__main__":
    from time import sleep
    pb=progressbarClass(8,"*")
    count=0
    while count<9:
        count+=1
        pb.progress(count)
        sleep(0.2)