#!/usr/bin/env python
#-*- coding:utf8 -*-

import os, sys

__all__ = [
    "ForkAsDaemon", 
    ]


'''将当前进程fork为一个守护进程

    注意：如果你的守护进程是由inetd启动的，不要这样做！inetd完成了
    所有需要做的事情，包括重定向标准文件描述符，需要做的事情只有
    chdir() 和 umask()了
'''
def ForkAsDaemon(stdin='/dev/null',stdout= '/dev/null', stderr= 'dev/null'):
    '''Fork当前进程为守护进程，重定向标准文件描述符
        （默认情况下定向到/dev/null）
    '''
    #Perform first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  #first parent out
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" %(e.errno, e.strerror))
        sys.exit(1)

    #从母体环境脱离
    os.chdir("/")
    os.umask(0)
    os.setsid()
    #执行第二次fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) #second parent out
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" %(e.errno,e.strerror))
        sys.exit(1)

    #进程已经是守护进程了，重定向标准文件描述符
    for f in sys.stdout, sys.stderr: f.flush()
    si = file(stdin, 'r')
    so = file(stdout,'a+')
    se = file(stderr,'a+',0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

if __name__ == "__main__":
    import time, datetime
    from xylog import *
    XYOpenLog("xyutil", XYLOG_TYPE_INFO, ".")
    XYLogInfo("before %s, %s", "world", datetime.datetime.now())

    ForkAsDaemon()

    XYOpenLog("xyutil", XYLOG_TYPE_INFO, ".")
    while True:
        XYLogInfo("hello %s, %s", "world", datetime.datetime.now())
        time.sleep(1)
