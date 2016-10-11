#!/usr/bin/env python
#-*- coding:utf8 -*-

import os
import logging
import datetime

__all__ = [
    "XYFlushLog", 
    "XYOpenLog", 
    "XYLogDebug", 
    "XYLogInfo", 
    "XYLogError", 
    "XYLOG_TYPE_ERROR", 
    "XYLOG_TYPE_INFO", 
    "XYLOG_TYPE_DEBUG", 
    ]

XYLOG_TYPE_ERROR = logging.ERROR
XYLOG_TYPE_INFO = logging.INFO
XYLOG_TYPE_DEBUG = logging.DEBUG

_log_name = ""
_log_level = XYLOG_TYPE_DEBUG
_log_path = "."
_log_file = ""
_logger = None
_log_handler = None


def XYFlushLog():
    """
        刷新日志配置
        """
    global _log_name
    global _log_level
    global _log_path
    global _log_file
    global _log_handler
    global _logger
#    file_name = datetime.datetime.now().strftime("%Y%m%d%H.log")
    file_name = datetime.datetime.now().strftime("%Y%m%d.log")
    if _log_file == file_name:
        return
    _log_file = file_name

#    logging.basicConfig(
#            filename = os.path.join(_log_path, file_name), 
#            level = _log_level, 
#            filemode = 'a', 
#            format = '%%(asctime)s <%s(%s)> %%(levelname)s: %%(message)s' % (_log_name, os.getpid())
#            )
    _logger = logging.getLogger('xy_' + _log_name)  
    if _log_handler:
        _logger.removeHandler(_log_handler)
    _log_handler = logging.FileHandler(os.path.join(_log_path, file_name), "a")
    _log_handler.setFormatter(logging.Formatter('%%(asctime)s <%s(%s)> %%(levelname)s: %%(message)s' % (_log_name, os.getpid())))
    _logger.addHandler(_log_handler)
    _logger.setLevel(_log_level)

def XYOpenLog(name, level, path):
    """
        日志初始化
        name:   日志名
        level:  日志等级，等级从高到低分别是XYLOG_TYPE_ERROR XYLOG_TYPE_INFO XYLOG_TYPE_DEBUG
        path:   日志文件存放位置
        """
    global _log_name
    global _log_level
    global _log_path
    _log_name = name
    _log_level = level
    _log_path = path
    XYFlushLog()


def XYLogDebug(msg, *args):
    """
        DEBUG级别日志
        """
    global _logger
    if _logger:
        XYFlushLog()
        _logger.debug(msg, *args)

def XYLogInfo(msg, *args):
    """
        INFO级别日志
        """
    global _logger
    if _logger:
        XYFlushLog()
        _logger.info(msg, *args)

def XYLogError(msg, *args):
    """
        ERROR级别日志
        """
    global _logger
    if _logger:
        XYFlushLog()
        _logger.error(msg, *args)

if __name__ == "__main__":
    import time
    XYOpenLog("xylog_test", XYLOG_TYPE_INFO, ".")
    for i in range(10):
        XYLogDebug("hello %s, %s", "world", "debug man")
        XYLogInfo("hello %s, %s", "world", "info man")
        XYLogError("hello %s, %s", "world", "error man")
        time.sleep(20)
