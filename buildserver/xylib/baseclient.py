#!/usr/bin/env python
#-*- coding:utf8 -*-

import os, socket
import ConfigParser
from xylog import *

__all__ = [
    "BaseClient", 
    ]

class BaseClient(object):
    """
        客户端基类，使用基于TCP的文本协议进行通信
        具体的业务逻辑，通过继承BaseClient，实现业务处理函数
        Demo:
            cli = BaseClient()
            cli.Init(ip = '192.168.9.237', port = 8002)
            cli.Send("1")
            print cli.Recv()

        """
    
    def __init__(self, config_file = None):
        self.socket = None
        self.recv_buffer_size = 1024
        self.config = None
        if config_file:
            self.InitWithConfig(config_file)

    def Init(self, ip, port):
        """
            客户端初始化逻辑
            """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.socket.connect((ip, port))  

    def InitWithConfig(self, config_file):
        """
            通过配置文件初始化
            """
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        ip = self.config.get("client", "ip")
        port = self.config.get("client", "port")
        self.Init(ip, port)

    def Send(self, buf):
        """
            发送数据
            """
        XYLogDebug("send begin ")
        self.socket.send(buf)

    def Recv(self):
        """
            接受数据
            """
        XYLogDebug("Recv begin ")
        return self.socket.recv(self.recv_buffer_size)


if __name__ == "__main__":

    XYOpenLog("SampleClient", XYLOG_TYPE_DEBUG, ".")

    class SampleClient(BaseClient):

        def Hello(self):
            XYLogDebug("SampleClient::Hello begin ")
            self.Send("1")
            buf = self.Recv()
            XYLogInfo("recv buf:" + buf)
            print buf

    cli = SampleClient()
    cli.Init(ip = '192.168.9.237', port = 8002)
    cli.Hello()
