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
envdata.currentmechinedict = dict()

envdata.receive_proclist = []           #接收到的命令系列
envdata.pre_commandlist = []            #分解成功的待处理命令系列
envdata.running_commandlist = []        #正在处理的命令系列
envdata.waitresult_list = []            #等待返回结果系列

envdata.databaselist = []       #支持的数据库服务器列表
envdata.proctollist = []        #支持的协议服务器列表

OVERTIME = 5                    #最大等待超时时间
OVERNUM = 3                     #最大重试次数

CMDDIR_ASK = 0
CMDDIR_REQUEST = 1

cmddirectdict = {
   CMDDIR_ASK:"CMDDIR_ASK",           \
   CMDDIR_REQUEST:"CMDDIR_REQUEST"
}

def proc_loginon(parameter):
    dataparmeter = dict(cmd="FUNC_LOGIN", machineid=parameter.get("machineid"))
    try:
        deviceid = envdata.databaseserver.databaseproc(dataparmeter)
    except (xmlrpc.client.Error, ConnectionRefusedError) as v:
        return("ERROR", v, "proc_loginon_get_deviceid")
    parameter['cmd'] = 'REQUEST_LOGINON'
    parameter['deviceid'] = deviceid
    try:
        deviceid = envdata.proctolserver.download_from_control(parameter)
    except (xmlrpc.client.Error, ConnectionRefusedError) as v:
        return("ERROR", v, "proc_loginon_request")
    return "SUCCESS"

def proc_cmdmax(parameter):
    return parameter

commandentry = dict(CMD_LOGINON=proc_loginon,\
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
    if envdata.proctolserver is None or envdata.databaseserver is None:
        pass
    else:
        try:
            templist = envdata.proctolserver.upload_to_control()
            if isinstance(templist, list) and templist:
                for tempdict in templist:
                    envdata.receive_proclist.append(tempdict)
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            pass
        finally:
            pass
    t = threading.Timer(2, timerfunc)
    t.start()

def funcproc():                          #将命令分解的分发函数
    while True:
        if len(envdata.receive_proclist) > 0:
            for functionitem in envdata.receive_proclist:
                if functionitem.get('function') == 'CMD_MAX':
                    pass
                else:
                    print(functionitem)
                    envdata.pre_commandlist.append(functionitem)
                    envdata.receive_proclist.remove(functionitem)

def pre_cmd_proc():
    while True:
        if len(envdata.pre_commandlist) > 0 and len(envdata.running_commandlist) == 0:
            tempdict = envdata.pre_commandlist.pop(0)
            tempdict["isrunned"] = False
            tempdict["overprocess"]=OVERNUM
            tempdict["overtime"]=time.time()+OVERTIME
            envdata.running_commandlist.append(tempdict)
        else:
            pass

def run_cmd_proc():
    while True:
        if len(envdata.running_commandlist) > 0:
            for task in envdata.running_commandlist:
                nowtime = time.time()
                if nowtime > task.get("overtime"):
                    if task.get("overprocess") > 0:
                        task["overprocess"] -= 1
                        task["isrunned"] = False
                        task["overtime"] += OVERTIME
                    else:
                        envdata.running_commandlist.remove(task)
                else:
                    if task.get("isrunned") == False:
                        result = proctolproc(task)
                        if result == "SUCCESS":
                            envdata.running_commandlist.remove(task)
                            break
                        else:
                            task["isrunned"] = True

def setup(func, funcname):
    env = Environment(loader=PackageLoader('webserver', 'templates'))
    template = env.get_template('choose.html')
    envdata.function = func
    envdata.functionname = funcname
    tempcontainer = '<form action="/running/initial.html" method="get">'
    tempcontainer += "<table>"
    tempcontainer +="<tr>"
    tempcontainer += "<th> </th>"
    tempcontainer += "<th>数据库序号</th>"
    tempcontainer += "<th>数据库名</th>"
    tempcontainer += "<th> </th>"
    tempcontainer += "<th>协议序号</th>"
    tempcontainer += "<th>协议名称</th>"
    tempcontainer +="</tr>"
    if len(envdata.databaselist) >= len(envdata.proctollist):
        templen = len(envdata.databaselist)
    else:
        templen = len(envdata.proctollist)
    for i in range(templen):
        tempcontainer += "<tr>"
        if(i < len(envdata.databaselist)):
            tempcontainer += "<td>"
            tempcontainer += '<input name="database_choose" type="radio" value="%s" />'% envdata.databaselist[i].get("id")
            tempcontainer += "</td>"
            tempcontainer += "<td>"
            tempcontainer += str(envdata.databaselist[i].get("id"))
            tempcontainer += "</td>"
            tempcontainer += "<td>"
            tempcontainer += envdata.databaselist[i].get("commit")
            tempcontainer += "</td>"
        else:
            tempcontainer += "<td>""</td>"
            tempcontainer += "<td>""</td>"
            tempcontainer += "<td>""</td>"
        if(i < len(envdata.proctollist)):
            tempcontainer += "<td>"
            tempcontainer += '<input name="proctol_choose" type="radio" value="%s" />'% envdata.proctollist[i].get("id")
            tempcontainer += "</td>"
            tempcontainer += "<td>"
            tempcontainer += str(envdata.proctollist[i].get("id"))
            tempcontainer += "</td>"
            tempcontainer += "<td>"
            tempcontainer += envdata.proctollist[i].get("name")
            tempcontainer += "</td>"
        else:
            tempcontainer += "<td>""</td>"
            tempcontainer += "<td>""</td>"
            tempcontainer += "<td>""</td>"
        tempcontainer += "</tr>"
    tempcontainer += "</table>"
    tempcontainer += '<input name="" type="submit" value="提交" />'
    tempcontainer += "</form>"
    return (template.render(top_name = '%s' % envdata.functionname,\
                name = '%s' % envdata.functionname,\
                choose_leftpage = tempcontainer))

def initial(dict_data):
    envdata.database = int(dict_data.get('database_choose'))
    envdata.proctol = int(dict_data.get('proctol_choose'))
    for database in envdata.databaselist:
        if database.get("id") == dict_data.get('database_choose'):
            envdata.databasename = database.get("name")
            envdata.databasecommit = database.get("commit")
            envdata.databaseserverinfo = (database.get("server"), int(database.get("port")))
            rpcserver = "http://%s:%s" % envdata.databaseserverinfo
            envdata.databaseserver = xmlrpc.client.ServerProxy(rpcserver)
    for proctol in envdata.proctollist:
        if proctol.get("id") == dict_data.get('proctol_choose'):
            envdata.proctolname = proctol.get("name")
            envdata.proctolserverinfo = (proctol.get("server"), int(proctol.get("port")))
            rpcserver = "http://%s:%s" % envdata.proctolserverinfo
            envdata.proctolserver = xmlrpc.client.ServerProxy(rpcserver)

    tempcontainer = ''
    tempfuncstr = ''
    dataparmeter = dict(cmd="FUNC_GET_ALLMACHINE")
    try:
        machinelist = envdata.databaseserver.databaseproc(dataparmeter)
        tempfuncstr += '<ul>%s：' % '在线的钥匙管理机'
        for machine in machinelist:
            if machine.__contains__("IsStop"):
                if machine.get('IsStop') == 0:
                    tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s:</a></li>' % ("CMD_CHANGE_TO_MACHINE",machine.get("MachineEquId"), machine.get("MachineName"))
        tempfuncstr += '</ul>'
        tempfuncstr += '<ul>%s：' % '不在线的钥匙管理机'
        for machine in machinelist:
            if machine.__contains__("IsStop"):
                if machine.get('IsStop') == 1:
                    tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s:</a></li>' % ("CMD_CHANGE_TO_MACHINE",machine.get("MachineEquId"), machine.get("MachineName"))
            else:
                tempfuncstr += '<li id=funcid><a href="/running/function.html?function=%s&MachineEquId=%s">%s:</a></li>' % ("CMD_CHANGE_TO_MACHINE",machine.get("MachineEquId"), machine.get("MachineName"))
        tempfuncstr += '</ul>'
    except (xmlrpc.client.Error, ConnectionRefusedError) as v:
        tempfuncstr = "error no database has!!!"

    templeftstr = '<ul>%s：' % envdata.functionname
    templeftstr += '<li>数据库采用：%s</li>' % envdata.databasecommit
    templeftstr += '<li>通讯协议采用：%s</li>' % envdata.proctolname
    templeftstr += '</ul>'

    env = Environment(loader=PackageLoader('webserver', 'templates'))
    template = env.get_template('running.html')
    return(template.render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templeftstr,\
                            function_page = tempfuncstr,\
                            name = '%s' % envdata.functionname,\
                            container_page = tempcontainer))

def proc_web_OTHER(parameter):
    pass

def proc_web_cmd_change_to_machine(parameter):
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
            tempfuncstr += '</ul>'
            env = Environment(loader=PackageLoader('webserver', 'templates'))
            template = env.get_template('running.html')
            return(template.render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templeftstr,\
                            function_page = tempfuncstr,\
                            name = '%s' % envdata.functionname,\
                            container_page = tempcontainer))
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            return "<h1> ERROR DATABASE </h1>"
    else:
        return "<h1> ERROR COMMAND </h1>"

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
    tempfuncstr += '</ul>'
    env = Environment(loader=PackageLoader('webserver', 'templates'))
    template = env.get_template('running.html')
    return [template, tempcontainer, tempfuncstr, templeftstr]

def proc_web_cmd_sendtimeto_machine(parameter):
    templist = currentmechinebase()
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'SEND_TIME'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送时间等待钥匙管理机接收"
            elif result == 'LINKERROR':
                templist[1] = "发送时间可能不成功，网络延迟"
            else:
                templist[1] = "发送时间不成功"
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
    else:
        templist[1] = "发送时间不成功,少了设备号"
    return(templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))


def proc_web_cmd_reset_machine(parameter):
    templist = currentmechinebase()
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'RESET_MACHINE'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送复位指令等待钥匙管理机接收"
            elif result == 'LINKERROR':
                templist[1] = "发送复位指令可能不成功，网络延迟"
            else:
                templist[1] =  "复位指令发送失败"
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
    else:
        templist[1] =  "复位指令发送失败,少了设备号"
    return(templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))

def proc_web_refresh_key(parameter):
    templist = currentmechinebase()
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'REFRESH_KEY'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送刷新钥匙指令等待钥匙管理机接收"
            elif result == 'LINKERROR':
                templist[1] = "发送刷新钥匙指令可能不成功，网络延迟"
            else:
                templist[1] = "钥匙刷新指令发送失败"
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
    else:
        templist[1] = "钥匙刷新指令发送失败,少了设备号"
    return(templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))

def proc_web_open_mechine(parameter):
    templist = currentmechinebase()
    if parameter.__contains__('MachineEquId'):
        machineid = parameter.get('MachineEquId')
        tempdict = dict()
        tempdict['cmd'] = 'OPEN_MECHINE'
        tempdict['machineid'] = machineid
        try:
            result = envdata.proctolserver.download_from_control(tempdict)
            if result == 'SUCCESS':
                templist[1] = "正确发送设备开门指令等待钥匙管理机接收"
            elif result == 'LINKERROR':
                templist[1] = "发送设备开门指令可能不成功，网络延迟"
            else:
                templist[1] = "设备开门指令发送失败"
        except (xmlrpc.client.Error, ConnectionRefusedError) as v:
            templist[1] = ("ERROR", v, "proc_loginon_request")
    else:
        templist[1] = "设备开门指令发送失败,少了设备号"
    return(templist[0].render(top_name = '%s' % envdata.functionname,\
                            choose_leftpage = templist[3],\
                            function_page = templist[2],\
                            name = '%s' % envdata.functionname,\
                            container_page = templist[1]))


webfuncentry = dict(CMD_CHANGE_TO_MACHINE=proc_web_cmd_change_to_machine,\
                    CMD_SENDTIMETO_MACHINE=proc_web_cmd_sendtimeto_machine,\
                    CMD_RESET_MACHINE=proc_web_cmd_reset_machine,\
                    CMD_REFRESH_KEY=proc_web_refresh_key,\
                    CMD_OPEN_MECHINE=proc_web_open_mechine,\
                    CMD_CHANGE_TO_OTHER=proc_web_OTHER)


def function(dict_data):
    if dict_data.__contains__('function'):
        envdata.receive_proclist.append(dict_data)
        #return webfuncentry[dict_data.get('function')](dict_data)
    else:
        return "<h1> ERROR COMMAND </h1>"

def beginrpc():
    with SimpleXMLRPCServer((envdata.server, envdata.port)) as server:
        server.register_function(setup)
        server.register_function(initial)
        server.register_function(function)
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
    funcproc_thread = threading.Thread(target=funcproc)
    funcproc_thread.daemon = True
    funcproc_thread.start()
    pre_command_thread = threading.Thread(target=pre_cmd_proc)
    pre_command_thread.daemon = True
    pre_command_thread.start()
    running_command_thread = threading.Thread(target=run_cmd_proc)
    running_command_thread.daemon = True
    running_command_thread.start()

def init_server():
    rpcserver = "http://%s:%s" % ("127.0.0.1", 40001)
    envdata.databaseserver = xmlrpc.client.ServerProxy(rpcserver)
    rpcserver = "http://%s:%s" % ("127.0.0.1", 30001)
    envdata.proctolserver = xmlrpc.client.ServerProxy(rpcserver)



def main():
    init_data()
    init_server()
    timerfunc()
    beginrpc()

if __name__ == "__main__":
    main()