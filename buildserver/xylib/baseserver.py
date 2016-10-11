#!/usr/bin/env python
#-*- coding:utf8 -*-

import os, socket, thread, sys
import time
import ConfigParser
from xylog import *
from xyutil import *

__all__ = [
    "BaseServer", 
    ]

class BaseServer(object):
    """
        服务端基类，使用基于TCP的文本协议进行通信
        具体的业务逻辑，通过继承BaseServer，重载OnRecv即可
        Demo:
            svr = BaseServer()
            svr.Init(ip = '192.168.9.237', port = 8002)
            svr.Run()

        or 
            svr = BaseServer()
            svr.InitWithConfig("server.conf")
            svr.Run()

        """
    
    def __init__(self):
        self.socket = None
        self.connect = None
        self.address = None
        self.recv_timeout = 5
        self.recv_buffer_size = 1024*16
        self.config = None

    def Init(self, ip, port):
        """
            服务器初始化逻辑
            """
        XYLogInfo("Init Server, ip %s port %d", ip, port)
#        ForkAsDaemon()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.socket.bind((ip, port))  
        self.socket.listen(5) 
        XYLogInfo("Server Init OK")
        sys.stderr.write("Server Init OK\n")

    def InitWithConfig(self, config_file):
        """
            通过配置文件初始化服务
            """
        XYLogInfo("InitWithConfig config_file %s", config_file)
        if not os.path.exists(config_file):
            XYLogInfo("config_file %s is not existed", config_file)
            sys.stderr.write("config_file %s is not existed\n" % config_file)
            sys.exit(1)

        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)

        try:
            ip = self.config.get("server", "ip")
        except Exception, e:
            XYLogInfo("config error, server label miss ip item")
            sys.stderr.write("config error, server label miss ip item") 
            sys.exit(1)
            
        try:
            port = int(self.config.get("server", "port"))
        except Exception, e:
            XYLogInfo("config error, server label miss port item")
            sys.stderr.write("config error, server label miss port item") 
            sys.exit(1)
        self.Init(ip, port)

    def NetworkFunction(self):
        """
            网络线程处理函数
            """
        XYLogDebug('Network function begin')
        while True:  
            self.connection,self.address = self.socket.accept()  
            try:  
                self.connection.settimeout(self.recv_timeout)  
                #self.connection.setSoTimeout(recv_timeout)
                buf = self.connection.recv(self.recv_buffer_size)  
                XYLogDebug("from " + self.address[0] + " recv " + buf)

                start_time = time.time()
                self.OnRecv(buf)
                cost_time = (time.time() - start_time) * 1000
                if cost_time > 100: # 100ms以上的运行耗时记录为INFO日志
                    XYLogInfo("OnRecv RUN: " + str(cost_time) + " ms")
                elif cost_time > 0.01: # 10us以内的运行耗时不打日志
                    XYLogDebug("OnRecv RUN: " + str(cost_time) + " ms")

            except socket.timeout:  
                XYLogError('recv data time out')
            self.connection.close() 
        XYLogDebug('Network function end')

    def Run(self):
        """
            运行服务，包括启动网络线程和定时更新逻辑
            """
        XYLogDebug("Run begin")
        try:
            XYLogInfo('start network thread')
            thread.start_new_thread(self.NetworkFunction, ())
        except Exception, e:
            XYLogError('start network thread error: %s' % (str(e)))

        XYLogDebug("Run ing")
        while True:
            start_time = time.time()
            ret = self.Update()
            cost_time = (time.time() - start_time) * 1000
            if cost_time > 100: # 100ms以上的运行耗时记录为INFO日志
                XYLogInfo("Update RUN: " + str(cost_time) + " ms")
            elif cost_time > 0.01: # 10us以内的运行耗时不打日志
                XYLogDebug("Update RUN: " + str(cost_time) + " ms")

            if ret != 1:
                time.sleep(5)
        XYLogDebug("Run end")

    def OnRecv(self, buf):
        """
            网络请求处理
            """
        XYLogDebug("OnRecv begin ")
        pass

    def Start(self):
        pass

    def Update(self):
        """
            逻辑更新
            """
        XYLogDebug("Update begin ")
        return 0


if __name__ == "__main__":

    XYOpenLog("SampleServer", XYLOG_TYPE_DEBUG, ".")

    class SampleServer(BaseServer):

        def OnRecv(self, buf):
            XYLogDebug("SampleServer::OnRecv begin ")
            if buf == '1':  
                self.connection.send('welcome to sample server!')  
            else:  
                self.connection.send('please go out!')  

    svr = SampleServer()
    #svr.Init(ip = '192.168.9.237', port = 8002)
    svr.Run()
