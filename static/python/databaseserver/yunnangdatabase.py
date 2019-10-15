# _*_ coding: utf-8 _*_
#用于输出

from xmlrpc.server import SimpleXMLRPCServer
import sys
from static.python.common import dbconnect, globaldata

SEVER_NAME = ('127.0.0.1', 40001)

envdata = globaldata.globel()
envdata.dbname = 'KMBSDB'
envdata.kma_keymachine = 'kma_keymachine'
envdata.kma_keymanager = 'kma_keymanager'
#各功能对应函数

envdata.CompanyID = 0
envdata.DepartmentId = 0


def proc_login(parameter):
    with dbconnect.DB(db = envdata.dbname) as db:
        deviceid=parameter.get('machineid')
        #sql = 'replace into KMBSDB.kma_keymachine(MachineEquId, MachineName, CompanyID, DepartmentId) values("%s","%s", %s, %s) '%(a,parameter.get("data").data.decode("GBK"),envdata.CompanyID,envdata.DepartmentId)
        sql = 'update kma_keymachine SET IsStop=0 where MachineEquId="%s"'%deviceid
        db.execute(sql)
        sql = 'select InUnitMachineEquId from KMBSDB.kma_keymachine where MachineEquId = "%s"'%deviceid
        db.execute(sql)
        result = db.fetchall()
        if result[0].get("InUnitMachineEquId") == None:
            return 0
        else:
            return result[0].get("InUnitMachineEquId")

def proc_get_allmachine(parameter):
     with dbconnect.DB(db = envdata.dbname) as db:
        sql = 'select * from KMBSDB.kma_keymachine'
        db.execute(sql)
        result = db.fetchall()
        resultlist = []
        for recode in result:
            tempdict = dict()
            for k,v in recode.items():
                if v != None:
                    tempdict[k] = v
            resultlist.append(tempdict)
        return resultlist

def proc_getmechineinfo(parameter):
    deviceid=parameter.get('machineid')
    with dbconnect.DB(db = envdata.dbname) as db:
        sql = 'select * from KMBSDB.kma_keymachine where MachineEquId="%s"'%deviceid
        db.execute(sql)
        result = db.fetchall()
        for recode in result:
            tempdict = dict()
            for k,v in recode.items():
                if v != None:
                    tempdict[k] = v
            return tempdict

def proc_max(parameter):
    result = {'error': 'Fault error in function'}
    return result

#初始化函数
def initial(**parameter):
    if parameter.__contains__('db'):
        envdata.dbname = parameter.get('db')
        envdata.kma_keymachine = 'kma_keymachine'
        envdata.kma_keymanager = 'kma_keymanager'
    else:
        envdata.dbname = 'KMBSDB'
        envdata.kma_keymachine = 'kma_keymachine'
        envdata.kma_keymanager = 'kma_keymanager'

commandentry = dict(FUNC_LOGIN=proc_login,\
                    FUNC_GET_ALLMACHINE=proc_get_allmachine,\
                    FUNC_GETMECHINEINFO=proc_getmechineinfo,\
                    FUNC_MAX=proc_max)

#命令分发函数
def databaseproc(parameter):
    #命令有效性判定
    if parameter.__contains__('cmd'):
        cmd = parameter.get('cmd')
    else:
        result = {'error': 'Fault error in command'}
        return result
    #解析指令并执行之
    if cmd in commandentry.keys():
        return commandentry[cmd](parameter)
    else:
        result = {'error': 'Fault error in command'}
        return result

def testprint():
    with dbconnect.DB(db = envdata.dbname) as db:
        sql = 'select * from KMBSDB.kma_keymachine where MachineEquId="3cf52620c168edc44dca548be4d2beab"'
        db.execute(sql)
        result = db.fetchall()
        for recode in result:
            tempdict = dict()
            for k,v in recode.items():
                if v != None:
                    tempdict[k] = v
            print(tempdict)

def begin():
    with SimpleXMLRPCServer(SEVER_NAME) as server:
        server.register_function(databaseproc)
        server.register_function(initial)
        server.register_function(testprint)
        #server.register_instance(service, allow_dotted_names=True)
        server.register_multicall_functions()
        print('Serving XML-RPC on ', SEVER_NAME)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)


if __name__ == "__main__":
    begin()
    #testprint()
