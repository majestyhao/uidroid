__author__ = 'Hao Fu'
#!/usr/bin/env python2
#-*-encoding:utf-8-*-

import datetime
import sys
import os

class __redirection__:

    def __init__(self):
        self.buff=''
        self.__console__=sys.stdout

    def write(self, output_stream):
        self.buff+=output_stream

    def to_console(self):
        sys.stdout=self.__console__
        print self.buff

    def to_file(self, file_path):
        f=open(file_path,'w')
        sys.stdout=f
        print self.buff
        f.close()

    def flush(self):
        self.buff=''

    def reset(self):
        sys.stdout=self.__console__

def diff_times_in_seconds(t1, t2):
    # caveat emptor - assumes t1 & t2 are python times, on the same day and t2 is after t1
    h1, m1, s1 = t1.hour, t1.minute, t1.second
    h2, m2, s2 = t2.hour, t2.minute, t2.second
    t1_secs = s1 + 60 * (m1 + 60*h1)
    t2_secs = s2 + 60 * (m2 + 60*h2)
    return(t2_secs - t1_secs)

import logging


logger = logging.getLogger('UiDroid-Console')
logger.setLevel(logging.DEBUG)

filehandler = logging.FileHandler('test.log')
filehandler.setLevel(logging.DEBUG)

consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)

logger.addHandler(filehandler)
logger.addHandler(consolehandler)

logger.info('foorbar')
o = os.popen('adb devices')
logger.info(o.readlines())

if __name__=="__main__":
    # redirection
    r_obj=__redirection__()
    sys.stdout=r_obj

    # get output stream
    print 'hello'
    print 'there'

    print os.system('adb devices')
    # using it
    print diff_times_in_seconds(datetime.datetime.strptime( "13:23:34", '%H:%M:%S').time(), datetime.datetime.strptime( "14:02:39", '%H:%M:%S').time())


    # redirect to console
    r_obj.to_console()

    # redirect to file
    r_obj.to_file('out.log')

    # flush buffer
    r_obj.flush()

    # reset
    r_obj.reset()





