#!/usr/bin/env python
#-*- coding:utf8 -*-

import sys, os ,commands 
import time, datetime, re
import ConfigParser
import json
from xylib import *
from _mysql import *
reload(sys)    
sys.setdefaultencoding('utf8')  

#Assign database var from conf file
HOST = ""
PORT = ""
USER = ""
PASSWORD = ""
DB = ""

etc_path=""
log_path=""
bin_path=""

class BuildHandler(object):
    def __init__(self):
        pass
    def Build(self):
        # 判断是否有暂停打包标记，有则停止打包
        if os.path.exists(r'pause.flag'):
            return

        try:
            mysql_util = MysqlUtil()
            mysql_util.Connect(HOST, USER, PASSWORD, DB, PORT)
            result = mysql_util.Query("select count(*) from build_list where status = 0")
            if not result or not result[0]:
                XYLogInfo("mysql error 1")
                return -1

            to_build_list_count = result[0]["count(*)"] 
            XYLogInfo("the number of task to build is %s" % (to_build_list_count))

            if to_build_list_count > 0:
                # 获取打包参数
                start_time = time.time()
                build_args_list = mysql_util.Query("select id,system_platform,debug_mode,project,ditch,branch,(now()-create_time) as spend_time,level,status from build_list where status = 0 order by level, id;")
                if not build_args_list:
                    XYLogInfo("mysql error 2")
                    return -2

                build_args = build_args_list[0]
                if(build_args['spend_time']<3):
                    return -1;
                
                rowCount = mysql_util.CUD("update build_list set status = 1 , begin_build_time = now() where id = %s and status = 0 "  % (build_args["id"]))
                #result = mysql_util.Execute("select count(*) from build_list where id adf")
                if rowCount != 1:
                    XYLogInfo("Update build status fail")
                    return -1
                cost_time = (time.time() - start_time) * 1000
                XYLogDebug("Build get_task RUN: " + str(cost_time) + " ms");


                # 执行打包脚本
#                 update_flag = "-q" if str(build_args["update_resource_flag"]) == "1" else ""
#                 if str(build_args["environment"]) == "2":
#                     environment = "t"
#                 elif str(build_args["environment"]) == "3":
#                     environment = "d"
#                 else:
#                     environment = "p"
                    
                debug_mode = "-d" if str(build_args["debug_mode"]) == "1" else "-r"
                system_platform = "android" if str(build_args["system_platform"])=="1" else "ios"

                start_time = time.time()
                command = "bash %s/autobuild.sh %s -u -b %s -p '%s' -i '%s' -s '%s' 2>&1 " \
                       % (bin_path,debug_mode,build_args["branch"] , build_args["project"], build_args["ditch"], system_platform)
                XYLogInfo(command)
#                build_log = os.popen(command).read()
                # 判断打包结果
                (errCode, build_log)=commands.getstatusoutput(command)
                build_log=build_log.decode('utf-8')
                
                cost_time = (time.time() - start_time) * 1000
                XYLogDebug("Build run_shell RUN: " + str(cost_time) + " ms" )
                
                if errCode==0 :
                    build_status=2
                else:
                    build_status=3
                    
                # 更新打包状态
                start_time = time.time()
                mysql_util.CUD("replace into build_log (id, create_time, build_log) values (%s, now(), '%s')" % (build_args["id"], Escape(build_log)))
                mysql_util.CUD("update build_list set status = %d , end_build_time = now() where id = %s" % (build_status, build_args["id"]))
                cost_time = (time.time() - start_time) * 1000
                XYLogDebug("Build update_result RUN: " + str(cost_time) + " ms");
                return 1
        except Exception, e:
            XYLogError("run build task error, reason [%s]" % (e))
        return 0
    def GetBranchList(self):
        branches_path = os.environ.get("BUILD_BRANCH_DIR")
#        if branches_path is None:
#            branches_path=DEFAULT_BUILD_PLATFORM_DIR
        #if platform_path.startswith("/"):
        branch_list = os.listdir(branches_path)
        if ".svn" in branch_list:
            branch_list.remove(".svn")
        for dir in branch_list:
            if not os.path.isdir(os.path.join(branches_path, dir)):
                print dir
                branch_list.remove(dir)
        return " ".join(branch_list);
    def GetProjectList(self):
        platform_path = os.environ.get("BUILD_PLATFORM_DIR")
#         if platform_path is None:
#             platform_path=DEFAULT_BUILD_PLATFORM_DIR
         #if platform_path.startswith("/"):
        platform_list = os.listdir(platform_path)
        if ".svn" in platform_list:
            platform_list.remove(".svn")
        for dir in platform_list:
            if not os.path.isdir(os.path.join(platform_path, dir)):
                platform_list.remove(dir)
        return " ".join(platform_list);
# 
    def GetProjectDict(self):
        platform_dict = {}
        platform_path = os.environ.get("BUILD_PLATFORM_DIR")
        if platform_path is None:
            platform_path=DEFAULT_BUILD_PLATFORM_DIR
        #if platform_path.startswith("/"):
        platform_list = os.listdir(platform_path)
        if ".svn" in platform_list:
            platform_list.remove(".svn")
        for platform in platform_list:
            ditch_path = os.path.join(platform_path, platform)
            if not os.path.isdir(ditch_path):
                continue
            ditch_list = os.listdir(ditch_path)
            if ".svn" in ditch_list:
                ditch_list.remove(".svn")
            for dir in ditch_list:
                if not os.path.isdir(os.path.join(ditch_path, dir)):
                    ditch_list.remove(dir)
            platform_dict[platform] = ditch_list
        return platform_dict
#     
#     def GetSDKProviderList(self):
#         platform_path = os.environ.get("BUILD_SDK_DIR")
#         if platform_path is None:
#             platform_path=DEFAULT_BUILD_SDK_DIR
#         #if platform_path.startswith("/"):
#         platform_list = os.listdir(platform_path)
#         if ".svn" in platform_list:
#             platform_list.remove(".svn")
#         return " ".join(platform_list);
#     
#     def GetDist(self,dir):
#         platform_dict = {}
#         platform_list = os.listdir(dir)
#         if ".svn" in platform_list:
#             platform_list.remove(".svn")
#         for platform in platform_list:
#             ditch_list = os.listdir(os.path.join(dir, platform))
#             if ".svn" in ditch_list:
#                 ditch_list.remove(".svn")
#             platform_dict[platform] = ditch_list
#         return platform_dict
# 
#     def GetSDKDist(self):
#         platform_path = os.environ.get("BUILD_SDK_DIR")
#         if platform_path is None:
#             platform_path=DEFAULT_BUILD_SDK_DIR
#         return self.GetDist(platform_path)
#     def GetPluginDist(self):
#         platform_path = os.environ.get("BUILD_PLUGIN_DIR")
#         if platform_path is None:
#             platform_path=DEFAULT_BUILD_PLUGIN_DIR
#         return self.GetDist(platform_path)
#         
#     
#     def GetDitchParams(self,platformName,ditchName):
#         resultJson = {}
#         resultJson["errCode"]=0
#         platform_dict = {}
#         platform_path = os.environ.get("BUILD_PLATFORM_DIR")
#         sdk_path=os.environ.get("BUILD_SDK_DIR")
#         plugin_path=os.environ.get("BUILD_PLUGIN_DIR")
#         if platform_path is None:
#             platform_path=DEFAULT_BUILD_PLATFORM_DIR
#         if sdk_path is None:
#             sdk_path=DEFAULT_BUILD_SDK_DIR
#         #if platform_path.startswith("/"):
#         platform_list = os.listdir(platform_path)
#         if ".svn" in platform_list:
#             platform_list.remove(".svn")
#         for platform in platform_list:
#             ditch_list = os.listdir(os.path.join(platform_path, platform))
#             if ".svn" in ditch_list:
#                 ditch_list.remove(".svn")
#             platform_dict[platform] = ditch_list
#         ditchSdkHelper = DitchSDKHelper(platform_path,sdk_path,plugin_path,platformName,ditchName);
#         initResult,errMsg=ditchSdkHelper.GetInitResult()
#         if not initResult:
#             resultJson["errCode"]=1
#             resultJson["errMsg"]=errMsg
#         else:
#             resultJson["ditchInfo"]=ditchSdkHelper.GetDitchJObject();
#             resultJson["sdk"]=ditchSdkHelper.GetSDKInfo();            
#             resultJson["plugin"]=ditchSdkHelper.GetPluginDefs();
#         return resultJson
#     
#     def GetSDKInfo(self,sdkProvider,version):
#         sdk_path=os.environ.get("BUILD_SDK_DIR")
#         if sdk_path is None:
#             sdk_path=DEFAULT_BUILD_SDK_DIR
#         return self.GetSDKDefinitions(sdk_path,sdkProvider,version)
# 
#     def GetPluginInfo(self,plugin,version):
#         sdk_path=os.environ.get("BUILD_PLUGIN_DIR")
#         if sdk_path is None:
#             sdk_path=DEFAULT_BUILD_SDK_DIR
#         return self.GetSDKDefinitions(sdk_path,plugin,version)
#         
#     def GetSDKDefinitions(self,sdk_path,path1,path2):
#         resultJson = {}
#         resultJson["errCode"]=1        
#         sdkUtil = SDKParamDefinitionUtil(sdk_path,path1,path2);
#         (initSuccess,errMsg)=sdkUtil.Init()
#         if initSuccess:
#             resultJson["errCode"]=0
#             resultJson['sdkInfo']=sdkUtil.GetSDKInfo();
#             return resultJson;
#         else:
#             resultJson["errMsg"]=errMsg
#         return resultJson
# 
#     def SaveDitchParams(self,platform,ditch,info):
#         resultJson = {}
#         resultJson["errCode"]=1;
#         platform_path = os.environ.get("BUILD_PLATFORM_DIR")
#         if platform_path is None:
#             platform_path=DEFAULT_BUILD_PLATFORM_DIR
#         ditchUtil = SDKParameterUtil(platform_path,platform,ditch)
#         ditchUtil.Init()
#         XYLogInfo("save ditch info is :{0}".format(info))
#         if ditchUtil.SaveDitchInfo(info):
#             resultJson["errCode"]=0;
#             command = "sh ./commitDitchParams.sh {0} {1} 2>&1".format(platform,ditch)
#             XYLogInfo(command)
#             #resultJson["errMsg"]=os.popen(command).read();
#             (errCode, output)=commands.getstatusoutput(command)
#             if errCode!=0 :
#                 resultJson["errCode"]=2
#                 resultJson["errMsg"]=output
#         return resultJson;
#     
#     def CreateNewDitch(self,platform,ditch):
#         resultJson={}
#         resultJson["errCode"]=1;
#         command = "sh ./autocreatenewditch.sh {0} {1} 2>&1".format(platform,ditch);
#         XYLogInfo(command)
#      #   command = "md "+self.GetPlatformDirPath()+"\\"+platform+"\\"+ditch
#         #(resultJson["errCode"], resultJson["errMsg"]) = commands.getstatusoutput("md asdf\\asdf")
#         #resultJson["errMsg"]=resultJson["errMsg"].decode('GB2312');
#         (resultJson["errCode"],resultJson["errMsg"])=commands.getstatusoutput(command)
# #        resultJson["errCode"]=0
#         return resultJson;
#     
#     def GetPlatformDirPath(self):
#         platform_path = os.environ.get("BUILD_PLATFORM_DIR")
#         if platform_path is None:
#             platform_path=DEFAULT_BUILD_PLATFORM_DIR
#         return platform_path
#     
#     def GetSDKDirPath(self):
#         sdk_path=os.environ.get("BUILD_SDK_DIR")
#         if sdk_path is None:
#             sdk_path=DEFAULT_BUILD_SDK_DIR
#         return sdk_path
#     
#     def UpdatePlatform(self):
#         command = "sh ./update_platform.sh 2>&1";
#         XYLogInfo(command)
#         return os.popen(command).read()
#     def UpdateSdk(self):
#         command = "sh ./update_sdk.sh 2>&1";
#         XYLogInfo(command)
#         return os.popen(command).read();
#     def UpdatePlugins(self):
#         command = "sh ./update_plugins.sh 2>&1";
#         XYLogInfo(command)
# 
#     def ModifyVersion(self, version, force_flag):
#         if not re.match("\d+\.\d+\.\d+", version):
#             XYLogError("ModifyVersion args error, version [%s]", version)
#         elif force_flag not in ("0", "1"):
#             XYLogError("ModifyVersion args error, force_flag [%s]", force_flag)
#         else:
#             command = "sh ./modify_version.sh '%s' %s 2>&1" % (version, force_flag);
#             XYLogInfo("ModifyVersion %s", command);
#             return os.popen(command).read()
#         return "ModifyVersion args error"
# 
#     def QueryVersion(self):
#         command = "sh ./query_version.sh 2>&1";
#         return os.popen(command).read()
# 
#     def CleanUpSvn(self):
#         command = "sh ./cleanupsvn.sh 2>&1";
#         XYLogInfo(command)
#         return os.popen(command).read()
# 
#     def GetRealDitchName(self,platform,ditch_name):
#         command = "sh ./get_real_ditch_name.sh %s %s 2>&1"%(platform,ditch_name);
#         XYLogInfo(command)
#         return os.popen(command).read()
    
    

class BuildServer(BaseServer):
    def __init__(self):
        BaseServer.__init__(self)
        self.handler = BuildHandler()
    
    def OnRecv(self, buf):
        args = buf.strip().split(" ")
        oper = args[0]
        XYLogInfo("oper: [%s]", oper)
        if oper == "test":
            XYLogInfo("test:%s", buf);
            self.connection.send("test:%s"%buf)
        if oper == "get_branch_list":
            self.connection.send(self.handler.GetBranchList());
        elif oper == "get_project_list":
            self.connection.send(self.handler.GetProjectList())
#         elif oper == "clean_up_svn":
#             self.connection.send(self.handler.CleanUpSvn())
        elif oper == "get_project_dict":
            self.connection.send(json.dumps(self.handler.GetProjectDict()))
#         elif oper == "get_sdk_list":
#             self.connection.send(self.handler.GetSDKProviderList()())
#         elif oper == "get_sdk_dict":
#             self.connection.send(json.dumps(self.handler.GetSDKDist()))
#         elif oper == "get_plugin_dict":
#             self.connection.send(json.dumps(self.handler.GetPluginDist()))
#         elif oper == "get_ditch_params":
#             if len(args) == 3:
#                 self.connection.send(json.dumps(self.handler.GetDitchParams(args[1],args[2])))
#         elif oper == "get_sdk_info":
#             if len(args) == 3:
#                 self.connection.send(json.dumps(self.handler.GetSDKInfo(args[1],args[2])))
#         elif oper == "get_plugin_info":
#             if len(args) == 3:
#                 self.connection.send(json.dumps(self.handler.GetPluginInfo(args[1],args[2])))
#         elif oper == "save_ditch_params" :
#             if(len(args) == 4):
#                 self.connection.send(json.dumps(self.handler.SaveDitchParams(args[1],args[2],args[3])));
#         elif oper == "create_new_ditch":
#             if(len(args)==3):
#                 self.connection.send(json.dumps(self.handler.CreateNewDitch(args[1],args[2])));
#         elif oper == "update_platform":
#             self.connection.send(self.handler.UpdatePlatform())
#         elif oper == "update_sdk":
#             self.connection.send(self.handler.UpdateSdk())
#         elif oper == "update_plugins":
#             self.connect.send(self.handler.UpdatePlugins())
#         elif oper == "query_version":
#             self.connection.send(self.handler.QueryVersion())
#         elif oper == "get_real_ditch_name":
#             if len(args)<3:
#                 self.connection.send("unknow")
#                 return
#             self.connection.send(self.handler.GetRealDitchName(args[1],args[2]))
#         elif oper == "modify_version":
#             if len(args) == 3:
#                 version = args[1]
#                 force_flag = args[2]
#                 result = self.handler.ModifyVersion(version, force_flag)
#             else:
#                 result = "the number of arguments error"
#                 XYLogError("modify_version, %s", result);
#             self.connection.send(result)
#         else:
#             msg = "oper not found: %s" % buf
#             XYLogError(msg)
#             self.connection.send(msg)

    
    def InitWithConfig(self, config_file):
        super(BuildServer,self).InitWithConfig(config_file)
        """通过配置文件初始化服务"""
        if not os.path.exists(config_file):
            XYLogInfo("config_file %s is not existed", config_file)
            sys.stderr.write("config_file %s is not existed\n" % config_file)
            sys.exit(1)
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        global HOST,PORT,USER,PASSWORD,DB
        try:
            HOST = self.config.get("db", "ip")
        except Exception, e:
            XYLogInfo("config error, db label miss ip item")
            sys.stderr.write("config error, db label miss ip item") 
            sys.exit(1)     
        try:
            PORT = int(self.config.get("db", "port"))
        except Exception, e:
            XYLogInfo("config error, db label miss port item")
            sys.stderr.write("config error, db label miss port item") 
            sys.exit(1)
      
        try:
            USER = self.config.get("db", "user")
        except Exception, e:
            XYLogInfo("config error, db label miss user item")
            sys.stderr.write("config error, db label miss user item") 
            sys.exit(1)  
            
        try:
            PASSWORD = self.config.get("db", "passwd")
        except Exception, e:
            XYLogInfo("config error, db label miss passwd item")
            sys.stderr.write("config error, db label miss passwd item") 
            sys.exit(1)
            
        try:
            DB = self.config.get("db", "db")
        except Exception, e:
            XYLogInfo("config error, db label miss db item")
            sys.stderr.write("config error, db label miss db item") 
            sys.exit(1)

    def Update(self):
        return self.handler.Build()


if __name__ == "__main__":
#    global etc_path
    etc_path = os.environ.get("BUILD_ETC_DIR")
#    global log_path
    log_path = os.environ.get("BUILD_LOG_DIR")
#    global bin_path
    bin_path = os.environ.get("BUILD_BIN_DIR")
    if log_path=="" or log_path is None:
        log_path="./logs"
    if etc_path==""  or etc_path is None:
        etc_path="./etc"
    if bin_path==""  or bin_path is None:
        bin_path="../bin"
#     if not log_path or log_path == "":
#         print "sys path BUILD_LOG_DIR is null, process exit"
#         sys.exit(-1)
    XYOpenLog("buildserver", XYLOG_TYPE_DEBUG, log_path)
    svr_config_file = os.path.join(etc_path, "buildserver.conf")
    svr = BuildServer()
    svr.InitWithConfig(svr_config_file)
    svr.Run()
