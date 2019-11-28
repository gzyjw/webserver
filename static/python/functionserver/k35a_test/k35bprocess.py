# _*_ coding: utf-8 _*_
#用于输出
from xmlrpc.server import SimpleXMLRPCServer
import sys
import threading
import xmlrpc.client
from jinja2 import Environment, PackageLoader
from static.python.common import globaldata
from xml.etree import ElementTree as ET
import time
import math



envdata = globaldata.globel()
envdata.server = ''                 #本服务器的地址
envdata.port = 0                    #本服务器的端口号
envdata.databasename = ''           #数据库服务器名连接用
envdata.databasecommit = ''         #数据库服务器名称
envdata.database = 0                #数据库序号
envdata.databaseserver = None       #数据库服务器
envdata.databaseserverinfo = None   #数据库服务器的地址及端口号
envdata.function = 0                #功能序号
envdata.functionname = ''           #功能名称
envdata.proctol = 0                 #协议服务器序号
envdata.proctolname = ''            #协议服务器名称
envdata.proctolserver = None        #协议服务器
envdata.proctolserverinfo = None    #协议服务器的地址及端口号
envdata.display = 0                 #显示服务器序号
envdata.displayname = ''            #显示服务器名称
envdata.displayserver = None        #显示服务器
envdata.displayserverinfo = None    #显示服务器的地址及端口号
envdata.currentmechinedict = dict()
envdata.webpageisready = False      #网页已准备好
envdata.webpage = ''                #网页内容
envdata.fontid = 1                  #字库序号
envdata.timeproc = None
envdata.funcproc = None
envdata.needflash = dict({"needfresh":False, "freshtime":0})           #不用刷新页面

envdata.receive_proclist = []           #接收到的命令系列
envdata.pre_commandlist = []            #分解成功的待处理命令系列
envdata.running_commandlist = []        #正在处理的命令系列
envdata.waitresult_list = []            #等待返回结果系列

envdata.databaselist = []       #支持的数据库服务器列表
envdata.proctollist = []        #支持的协议服务器列表
envdata.displaylist = []        #支持的显示服务器列表
envdata.fontfilelist = []       #支持的字库列表
envdata.progfilelist = []       #支持的固件列表

OVERTIME = 5                    #最大等待超时时间
OVERNUM = 3                     #最大重试次数
TIME_DELAY = 0.2                #线程空闲时间

CMDDIR_ASK = 0
CMDDIR_REQUEST = 1

cmddirectdict = {
   CMDDIR_ASK:"CMDDIR_ASK",           \
   CMDDIR_REQUEST:"CMDDIR_REQUEST"
}

k35funclist = tuple([{"cmd_name":"CMD_LOGINON", "cmd_commit":"注册"},\
                    {"cmd_name":"CMD_SENDTIMETO_MACHINE", "cmd_commit":"校时"},\
                    {"cmd_name":"CMD_RESET_MACHINE", "cmd_commit":"复位"},\
                    {"cmd_name":"CMD_REFRESH_KEY", "cmd_commit":"刷新钥匙"},\
                    {"cmd_name":"CMD_OPEN_MECHINE", "cmd_commit":"开门"},\
                    {"cmd_name":"CMD_UPDATE_FONT", "cmd_commit":"升级字库"},\
                    {"cmd_name":"CMD_UPDATE_PROG", "cmd_commit":"升级固件"},\
                    {"cmd_name":"CMD_GETKEYINFO", "cmd_commit":"读取钥匙信息"},\
                    {"cmd_name":"CMD_ALLKEY_STATUS", "cmd_commit":"所有钥匙状态"}])


def getserver(parameter):
    envdata.database = int(parameter.get('databaselist'))
    envdata.proctol = int(parameter.get('proctollist'))
    for database in envdata.databaselist:
        if database.get("id") == parameter.get('databaselist'):
            envdata.databasename = database.get("name")
            envdata.databasecommit = database.get("commit")
            envdata.databaseserverinfo = (database.get("server"), int(database.get("port")))
            rpcserver = "http://%s:%s" % envdata.databaseserverinfo
            envdata.databaseserver = xmlrpc.client.ServerProxy(rpcserver)
    for proctol in envdata.proctollist:
        if proctol.get("id") == parameter.get('proctollist'):
            envdata.proctolname = proctol.get("name")
            envdata.proctolserverinfo = (proctol.get("server"), int(proctol.get("port")))
            rpcserver = "http://%s:%s" % envdata.proctolserverinfo
            envdata.proctolserver = xmlrpc.client.ServerProxy(rpcserver)
    for display in envdata.displaylist:
        if display.get("id") == parameter.get('displaylist'):
            envdata.displayname = display.get("name")
            envdata.displayserverinfo = (display.get("server"), int(display.get("port")))
            rpcserver = "http://%s:%s" % envdata.displayserverinfo
            envdata.displayserver = xmlrpc.client.ServerProxy(rpcserver)

def proc_loginon(parameter):
    dataparmeter = dict(cmd="FUNC_LOGIN", machineid=parameter.get("machineid"))
    tempparameter = dict()
    try:
        deviceid = envdata.databaseserver.databaseproc(dataparmeter)
    except (xmlrpc.client.Error, ConnectionRefusedError) as v:
        return("ERROR", v, "proc_loginon_get_deviceid")
    tempparameter['cmd'] = 'REQUEST_LOGINON'
    tempparameter['deviceid'] = deviceid
    tempparameter['machineid'] = parameter['machineid']
    tempparameter['timestamp'] = parameter['timestamp']
    try:
        deviceid = envdata.proctolserver.download_from_control(tempparameter)
    except (xmlrpc.client.Error, ConnectionRefusedError) as v:
        return("ERROR", v, "proc_loginon_request")
    return "SUCCESS"

def proc_change_to_machine(parameter):
    if parameter.__contains__('MachineEquId'):
        dataparmeter = dict(cmd="FUNC_GETMECHINEINFO", machineid=parameter.get("MachineEquId"))
        try:
            envdata.currentmechinedict.update(envdata.databaseserver.databaseproc(dataparmeter))
            tempcontainer = ''
            tempfuncstr = ''
            templeftstr = '<ul>%s：' % envdata.functionname
            templeftstr += '<li>数据库采用：%s</li>' % envdata.databasecommit
            templeftstr += '<li>通讯协议采用：%s</li>' % envdata.proctolname
            templeftstr += '</ul>'
            tempfuncstr += '<ul>%s功能：' % envdata.currentmechinedict.get('MachineName')
            tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                           % ("CMD_SENDTIMETO_MACHINE",envdata.currentmechinedict.get("MachineEquId"), '校时')
            tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                           % ("CMD_RESET_MACHINE",envdata.currentmechinedict.get("MachineEquId"), '复位')
            tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                           % ("CMD_REFRESH_KEY",envdata.currentmechinedict.get("MachineEquId"), '刷新钥匙')
            tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                           % ("CMD_OPEN_MECHINE",envdata.currentmechinedict.get("MachineEquId"), '开设备门')
            tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                            % ("CMD_UNLOCK_ALLKEY",envdata.currentmechinedict.get("MachineEquId"), '全部解锁')
            tempfuncstr += '</ul>'
            env = Environment(loader=PackageLoader('webserver', 'templates'))
            template = env.get_template('running.html')
            envdata.webpageisready = True
            envdata.webpage = (template.render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templeftstr,\
                            function_page = tempfuncstr,\
                            name = '%s' % envdata.functionname,\
                            container_page = tempcontainer))
            return 'SUCCESS'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            envdata.webpageisready = True
            envdata.webpage =  "<h1> ERROR DATABASE </h1>"
            return 'ERROR'
    else:
        envdata.webpageisready = True
        envdata.webpage =  "<h1> ERROR COMMAND </h1>"
        return 'ERROR'

def currentmechinebase():
    tempcontainer = ''
    tempfuncstr = ''
    templeftstr = '<ul>%s：' % envdata.functionname
    templeftstr += '<li>数据库采用：%s</li>' % envdata.databasecommit
    templeftstr += '<li>通讯协议采用：%s</li>' % envdata.proctolname
    templeftstr += '</ul>'
    tempfuncstr += '<ul>%s功能：' % envdata.currentmechinedict.get('MachineName')
    tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                % ("CMD_SENDTIMETO_MACHINE",envdata.currentmechinedict.get("MachineEquId"), '校时')
    tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                % ("CMD_RESET_MACHINE",envdata.currentmechinedict.get("MachineEquId"), '复位')
    tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                % ("CMD_REFRESH_KEY",envdata.currentmechinedict.get("MachineEquId"), '刷新钥匙')
    tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                % ("CMD_OPEN_MECHINE",envdata.currentmechinedict.get("MachineEquId"), '开设备门')
    tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s</a></li>' \
                % ("CMD_UNLOCK_ALLKEY",envdata.currentmechinedict.get("MachineEquId"), '全部解锁')
    tempfuncstr += '</ul>'
    env = Environment(loader=PackageLoader('webserver', 'templates'))
    template = env.get_template('running.html')
    return [template, tempcontainer, tempfuncstr, templeftstr]



def proc_sendtimeto_machine(parameter):
    getserver(parameter)
    res = ''
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'SEND_TIME'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                res = 'LINKERROR'
            else:
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            res = 'ERROR'
    else:
        res = 'ERROR'
    return res

def proc_reset_machine(parameter):
    templist = currentmechinebase()
    res = ''
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'RESET_MACHINE'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送复位指令等待钥匙管理机接收"
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                templist[1] = "发送复位指令可能不成功，网络延迟"
                res = 'LINKERROR'
            else:
                templist[1] =  "复位指令发送失败"
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
            res = 'ERROR'
    else:
        templist[1] =  "复位指令发送失败,少了设备号"
        res = 'ERROR'
    envdata.webpageisready = True
    envdata.webpage = (templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))
    return res

def proc_refresh_key(parameter):
    templist = currentmechinebase()
    res = ''
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'REFRESH_KEY'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送刷新钥匙指令等待钥匙管理机接收"
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                templist[1] = "发送刷新钥匙指令可能不成功，网络延迟"
                res = 'LINKERROR'
            else:
                templist[1] = "钥匙刷新指令发送失败"
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
            res = 'ERROR'
    else:
        templist[1] = "钥匙刷新指令发送失败,少了设备号"
        res = 'ERROR'
    envdata.webpageisready = True
    envdata.webpage = (templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))
    return res

def proc_open_mechine(parameter):
    templist = currentmechinebase()
    res = ''
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'OPEN_MECHINE'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送设备开门指令等待钥匙管理机接收"
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                templist[1] = "发送设备开门指令可能不成功，网络延迟"
                res = 'LINKERROR'
            else:
                templist[1] = "设备开门指令发送失败"
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
            res = 'ERROR'
    else:
        templist[1] = "设备开门指令发送失败,少了设备号"
        res = 'ERROR'
    envdata.webpageisready = True
    envdata.webpage = (templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))
    return res

def proc_unlock_allkey(parameter):
    res = ''
    templist = currentmechinebase()
    res = ''
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'UNLOCK_ALLKEY'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送全解锁指令等待钥匙管理机接收"
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                templist[1] = "发送全解锁指令可能不成功，网络延迟"
                res = 'LINKERROR'
            else:
                templist[1] = "全解锁指令发送失败"
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
            res = 'ERROR'
    else:
        templist[1] = "全解锁指令发送失败,少了设备号"
        res = 'ERROR'
    envdata.webpageisready = True
    envdata.webpage = (templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))
    return res

def proc_heart(parameter):
    res = ''
    templist = currentmechinebase()
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'BREAK_HEART'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送全解锁指令等待钥匙管理机接收"
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                templist[1] = "发送全解锁指令可能不成功，网络延迟"
                res = 'LINKERROR'
            else:
                templist[1] = "全解锁指令发送失败"
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
            res = 'ERROR'
    else:
        templist[1] = "全解锁指令发送失败,少了设备号"
        res = 'ERROR'
    envdata.webpageisready = True
    envdata.webpage = (templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))
    return res

def proc_allkey_status(parameter):
    getserver(parameter)
    res = ''
    if (parameter.__contains__('MachineEquId')) :
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'ALLKEY_STATUS'
        tempdict['machineid'] = machineid

        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                res = 'LINKERROR'
            else:
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            res = 'ERROR'
    else:
        res = 'ERROR'
    return res

def proc_update_font(parameter):
    getserver(parameter)
    res = ''
    if parameter.__contains__('MachineEquId') and (parameter.__contains__('fontfilelist')):
        tempdict = dict()
        tempdict['cmd'] = 'UPDATE_FONT'
        tempdict['machineid'] = parameter.get('MachineEquId')
        for fontfile in envdata.fontfilelist:
            if fontfile.get("id") == parameter.get('fontfilelist'):
                with open("../../../fontdir/" +fontfile.get("path"), "rb") as f:
                    buff = f.read()
                    tempbcc = 0
                    for item in buff:
                        tempbcc = tempbcc ^ item
                    tempdict['fontdata'] = buff
                    tempdict['fontbcc'] = tempbcc
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                res = 'LINKERROR'
            else:
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            res = 'ERROR'
    else:
        res = 'ERROR'
    return res


def proc_update_prog(parameter):
    getserver(parameter)
    res = ''
    if parameter.__contains__('MachineEquId') and (parameter.__contains__('progfilelist')):
        tempdict = dict()
        tempdict['cmd'] = 'UPDATE_PROG'
        tempdict['machineid'] = parameter.get('MachineEquId')
        for progfile in envdata.progfilelist:
            if progfile.get("id") == parameter.get('progfilelist'):
                with open("../../../progdir/" +progfile.get("path"), "rb") as f:
                    buff = f.read()
                    tempbcc = 0
                    for item in buff:
                        tempbcc = tempbcc ^ item
                    tempdict['progdata'] = buff
                    tempdict['progbcc'] = tempbcc
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                res = 'SUCCESS'
            elif result == 'LINKERROR':
                res = 'LINKERROR'
            else:
                res = 'ERROR'
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            res = 'ERROR'
    else:
        res = 'ERROR'
    return res

def proc_cmdmax(parameter):
    return parameter

commandentry = dict(CMD_LOGINON=proc_loginon,\
                    CMD_CHANGE_TO_MACHINE=proc_change_to_machine,\
                    CMD_SENDTIMETO_MACHINE=proc_sendtimeto_machine,\
                    CMD_RESET_MACHINE=proc_reset_machine,\
                    CMD_REFRESH_KEY=proc_refresh_key,\
                    CMD_OPEN_MECHINE=proc_open_mechine,\
                    CMD_UNLOCK_ALLKEY=proc_unlock_allkey,\
                    CMD_HEART=proc_heart,\
                    CMD_ALLKEY_STATUS=proc_allkey_status,\
                    CMD_UPDATE_FONT=proc_update_font,\
                    CMD_UPDATE_PROG=proc_update_prog,\

                    CMD_MAX=proc_cmdmax)


def proctolproc(parameter):
    if parameter.__contains__('function'):
        function = parameter.get('function')
    else:
        result = {'error': 'Fault error in command'}
        return result
    #解析指令并执行之
    if function in commandentry.keys():
        return commandentry[function](parameter)
    else:
        result = {'error': 'Fault error in command'}
        return result


def timerfunc():
    while True:
        if envdata.proctolserver is None or envdata.databaseserver is None:
            pass
        else:
            try:
                templist = envdata.proctolserver.upload_to_control()
                if isinstance(templist, list) and templist:
                    for tempdict in templist:
                        envdata.receive_proclist.append(tempdict)
            except (xmlrpc.client.Error, ConnectionRefusedError, BaseException) as v:
                pass
            finally:
                pass
        time.sleep(2)


def funcproc():                          #将命令分解的分发函数
    while True:
        try:
            wait_result_proc()
            run_cmd_proc()
            pre_cmd_proc()
            if len(envdata.receive_proclist) > 0:
                for functionitem in envdata.receive_proclist:
                    if functionitem.get('function') in commandentry.keys():
                        envdata.pre_commandlist.append(functionitem)
                    envdata.receive_proclist.remove(functionitem)
            temptime = time.time()
            if temptime > envdata.needflash.get("freshtime"):
                envdata.needflash["freshtime"] = temptime + 2
        except Exception:
            pass
        #time.sleep(0.01)

def heartproc():
    if envdata.proctolserver is None:
        pass
    else:
        tempcommand = dict()
        tempcommand["function"] = "CMD_HEART"
        tempcommand["MachineEquId"] = envdata.currentmechinedict.get("MachineEquId")
        if tempcommand["MachineEquId"] == None:
            pass
        else:
            function_x(tempcommand)
    global t
    t = threading.Timer(12, heartproc)
    t.start()

def pre_cmd_proc():
    try:
        if len(envdata.pre_commandlist) > 0 and len(envdata.running_commandlist) == 0:
            tempdict = envdata.pre_commandlist.pop(0)
            tempdict["isrunned"] = False
            tempdict["overprocess"]=OVERNUM
            tempdict["overtime"]=time.time()+OVERTIME
            envdata.running_commandlist.append(tempdict)
        else:
            pass
    except Exception:
        pass

def run_cmd_proc():
    try:
        if len(envdata.running_commandlist) > 0:
            for task in envdata.running_commandlist:
                nowtime = time.time()
                if nowtime > task.get("overtime"):
                    if task.get("overprocess") > 0:
                        task["overprocess"] -= 1
                        task["isrunned"] = False
                        task["overtime"] += OVERTIME
                    else:
                        print(task.get('function'), "del from running_commandlist")
                        envdata.running_commandlist.remove(task)
                else:
                    if task.get("isrunned") == False:
                        print(task.get('function'), "in running")
                        result = proctolproc(task)
                        if result == "SUCCESS":
                            envdata.running_commandlist.remove(task)
                            task["overtime"] = time.time() + OVERTIME
                            envdata.waitresult_list.append(task)
                            break
                        else:
                            task["isrunned"] = True
    except Exception:
        pass

def wait_result_proc():
    try:
        if len(envdata.waitresult_list) >0:
            for task in envdata.waitresult_list:
                if time.time() > task["overtime"]:
                    print("del task", task['function'])
                    envdata.waitresult_list.remove(task)
    except Exception:
        pass

def setup():
    tempdict = dict()
    tempdict["index"] = dict(databaselist = "支持的数据库", proctollist = "支持的协议", displaylist = "支持的显示界面")
    tempdict["databaselist"] = envdata.databaselist
    tempdict["proctollist"] = envdata.proctollist
    tempdict["displaylist"] = envdata.displaylist
    return tempdict

def initial(dict_data):
    tempstr = "/running.html?"
    for k,v in dict_data.items():
        tempstr += '%s=%s&'%(k, v)
    tempstr += 'function=CMD_DISPLAYINITIAL&timestamp=%s'%time.time()
    return tempstr

def proc_web_OTHER(parameter):
    pass

def begin(dict_data):
    getserver(dict_data)
    dataparmeter = dict(cmd="FUNC_GETMECHINEINFO", machineid=dict_data["machineid"])
    try:
        machinelist = envdata.databaseserver.databaseproc(dataparmeter)
        dict_data["MachineEquId"] = machinelist["MachineEquId"]
    except (xmlrpc.client.Error, ConnectionRefusedError) as v:
        tempfuncstr = "error no database has!!!"

    dict_data["viewstage"] = "respecnce"
    dict_data["functionlist"] = k35funclist
    return dict_data

def function_x(dict_data):
    getserver(dict_data)
    if dict_data.__contains__('function'):
        if dict_data["function"] == "CMD_DISPLAYINITIAL":
            templist = envdata.displayserver.initial(dict_data)
            tempdict = dict()
            tempdict["returnresult"] = "freshpage"
            tempdict["data"] = templist
            return tempdict
        elif dict_data["function"] == "CMD_FRESHDISPLAY":
            templist = []
            tempdict = dict()
            tempdict["returnresult"] = "donotchange"
            tempdict["data"] = templist
            return tempdict
        else:
            envdata.receive_proclist.append(dict_data)
            dict_data["returnresult"] = "commandissend"
    else:
        dict_data["returnresult"] = "commandnot"
    dict_data["functionlist"] = k35funclist
    return dict_data

def returnstatus(dict_data):
    tempdict = dict(result="success", parameter="gzyjw")
    return tempdict

def beginrpc():
    with SimpleXMLRPCServer((envdata.server, envdata.port)) as server:
        server.register_function(setup)
        server.register_function(initial)
        #server.register_function(function, 'function')
        server.register_function(function_x, 'function')
        server.register_function(begin, 'begin')
        server.register_function(returnstatus)
        #server.register_instance(service, allow_dotted_names=True)
        server.register_multicall_functions()
        print('Serving XML-RPC on localhost port 20001')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

def init_data():
    str_xml = open('config.xml', 'r').read()
    root = ET.XML(str_xml)
    envdata.server = root.attrib['addr']
    envdata.port = int(root.attrib['port'])
    for item in root:
        for subitem in item.iter('DATABASE'):
            envdata.databaselist.append(subitem.attrib)
        for subitem in item.iter('PROCTOL'):
            envdata.proctollist.append(subitem.attrib)
        for subitem in item.iter('DISPLAY'):
            envdata.displaylist.append(subitem.attrib)
        for subitem in item.iter('FONTFILE'):
            envdata.fontfilelist.append(subitem.attrib)
        for subitem in item.iter('PROGFILE'):
            envdata.progfilelist.append(subitem.attrib)
    heartproc()


def init_server():
    rpcserver = "http://%s:%s" % ("127.0.0.1", 40001)
    envdata.databaseserver = xmlrpc.client.ServerProxy(rpcserver)
    rpcserver = "http://%s:%s" % ("127.0.0.1", 30001)
    envdata.proctolserver = xmlrpc.client.ServerProxy(rpcserver)
    rpcserver = "http://%s:%s" % ("127.0.0.1", 50001)
    envdata.displayserver = xmlrpc.client.ServerProxy(rpcserver)
'''
def checkprocess():
    while True:
        if envdata.funcproc._is_stopped:
            print('funcproc is stopped')
            envdata.funcproc._stop()
            envdata.funcproc.start()
        if envdata.timeproc._is_stopped:
            print("timeproc is stopped")
        time.sleep(1)
'''

def main():
    init_data()
    init_server()
    envdata.timeproc = threading.Thread(target=timerfunc)
    envdata.timeproc.setDaemon(True)
    envdata.timeproc.start()
    envdata.funcproc = threading.Thread(target=funcproc)
    envdata.funcproc.setDaemon(True)
    envdata.funcproc.start()
    #p = threading.Thread(target=checkprocess)
    #p.setDaemon(True)
    #p.start()
    beginrpc()

if __name__ == "__main__":
    main()
