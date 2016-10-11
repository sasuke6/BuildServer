#!/usr/bin/env python
#-*- coding:utf8 -*-

import MySQLdb

__all__ = [
    "Escape", 
    "ExecuteSql", 
    "MysqlUtil", 
    ]

def Escape(content):
    """
        转义MySQL字符串
        """
    return MySQLdb.escape_string(content)

def ExecuteSql(host, user, password, db, port, sql):
    """
        执行MySQL语句
        """
    conn = MySQLdb.connect(host=host, user=user, passwd=password, db=db, port=port)
    cur=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cur.execute('SET NAMES UTF8')
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result

class MysqlUtil(object):
    """
        MySQL 接口类
        包装了MySQL常用操作
        """
    def __init__(self):
        self.connect = None
        self.cursor = None

    def __del__(self):
        self.Close()

    def Close(self):
        """
            关闭MySQL连接
            """
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connect:
            self.connect.close()
            self.connect = None

    def Connect(self, host, user, password, db, port):
        """
            建立MySQL连接 
            """
        self.Close()
        self.connect = MySQLdb.connect(host=host, user=user, passwd=password, db=db, port=port)
        self.cursor = self.connect.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        self.cursor.execute('SET NAMES UTF8')

    def Execute(self, sql):
        """
            执行MySQL语句，返回字典和行数
            """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.connect.commit()
        return result,self.cursor.rowcount
    
    def Query(self, sql):
        """
            执行MySQL语句，返回字典
            """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.connect.commit()
        return result
    
    def CUD(self,sql):
        """
            执行MySQL语句，返回行数
            """
        self.cursor.execute(sql)
        self.cursor.fetchall()
        self.connect.commit()
        return self.cursor.rowcount
    

        

if __name__ == "__main__":
    print "ExecuteSql"
    print ExecuteSql("192.168.7.186", "compile", "123456", "compile", 4580, "select * from build_list limit 1")

    print "MysqlUtil"
    mysql_util = MysqlUtil()
    mysql_util.Connect("192.168.7.186", "compile", "123456", "compile", 4580)
    print mysql_util.Execute("show tables")
    print mysql_util.Execute("select * from build_list limit 2")
