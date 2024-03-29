import socketserver
from threading import Thread
import threading
import time
from xmlrpc.server import SimpleXMLRPCServer
import sys

from static.python.common import globaldata


#for no machinaID
import hashlib

envdata = globaldata.globel()



TCP_PORT = 10003
BUFSIZE = 4096

SEVER_NAME = ('127.0.0.1', 30001)

g_conn_pool = []


upload_pool = []
download_pool = []

envdata.receive_proclist = []           #接收到的命令系列
envdata.pre_commandlist = []            #已上送的接收命令系列
envdata.send_proclist = []              #待发送的命令系列
envdata.pre_send_proclist = []          #分解成功的命令队列
envdata.running_commandlist = []        #正在处理的命令系列
envdata.waitresult_list = []            #等待返回结果系列

envdata.max = 0

OVERTIME = 10                    #最大等待超时时间
OVERNUM = 3                     #最大重试次数
TIME_DELAY = 0.2                #线程空闲时间


onlinekeymachine = dict()

#E40proctol parameter

#站类型
ADDR_TYPE_UT = 100
ADDR_TYPE_GC = 110
#响应标记
RESP_FLAG = 0x80
#帧标识
CTRL_WORD_SEND = 0x40 #主动发送帧
CTRL_WORD_RESP = 0x80 #应答帧
CTRL_WORD_ACK =  0x81 #ACK,NAK帧
# 命令字
CMD_LMO = 0x00 # 链路维护命令
CMD_KMG = 0x0A # 钥匙管理机相关命令集
#=================
CMD_GP = 0x01  #链路维护命令
CMD_GP_JS = 0x7F  #链路维护命令
CMD_GP_UP = 0x7E  #链路维护命令
CMD_GP_DOWN = 0x7D  #链路维护命令
# 功能码
FUNC_LOGIN = 0x00 # 注册
FUNC_HB = 0x01 # 心跳检测
FUNC_TIMING = 0x02 # 校时

FUNC_KEY_STATE = 0x01 # 管理机发送单个钥匙状态
FUNC_QUERY_STATE = 0x02
FUNC_UPLOAD_STATE = 0x03
FUNC_QUERY_REC = 0x04
FUNC_UPLOAD_REC = 0x05

FUNC_DOWNLOAD_TASKINFO = 0x07
FUNC_DOWNLOAD_TASK_LEN = 0x08
FUNC_DOWNLOAD_TASK_CTX = 0x09
FUNC_DELETE_TASK = 0x0A

FUNC_DOWNLOAD_USERINFO_LEN = 0x0B
FUNC_DOWNLOAD_USERINFO_CTX = 0x0C

FUNC_UPLOAD_KEYSINFO_LEN = 0x0D
FUNC_UPLOAD_KEYSINFO_CTX = 0x0E
FUNC_DOWNLOAD_KEYSINFO_LEN = 0x0f
FUNC_DOWNLOAD_KEYSINFO_CTX = 0x10

FUNC_UPGRADE_LEN = 0x11
FUNC_UPGRADE_CTX = 0x12
FUNC_FONT_LEN = 0x13
FUNC_FONT_CTX = 0x14
FUNC_UPLOAD_SYS_CFG_LEN = 0x15
FUNC_UPLOAD_SYS_CFG_CTX = 0x16
FUNC_SET_SYS_CFG_LEN = 0x1d
FUNC_SET_SYS_CFG_CTX = 0x1e
FUNC_UPLOAD_USER_CFG_LEN = 0x17
FUNC_UPLOAD_USER_CFG_CTX = 0x18
FUNC_SET_USER_CFG_LEN = 0x1f
FUNC_SET_USER_CFG_CTX = 0x20
FUNC_UPLOAD_KEY_CFG_LEN = 0x19
FUNC_UPLOAD_KEY_CFG_CTX = 0x1a
FUNC_SET_KEY_CFG_LEN = 0x21
FUNC_SET_KEY_CFG_CTX = 0x22
FUNC_UPLOAD_UNLOCK_CFG_LEN = 0x1b
FUNC_UPLOAD_UNLOCK_CFG_CTX = 0x1c
FUNC_SET_UNLOCK_CFG_LEN = 0x23
FUNC_SET_UNLOCK_CFG_CTX = 0x24

FUNC_REBOOT = 0x25
FUNC_AUTO_SET_KEY = 0x26
FUNC_OPEN_DOOR = 0x27
FUNC_FORMAT_NANDFLASH = 0x28
FUNC_UPLOAD_RFID = 0x29
FUNC_GET_BUILDTIME = 0x2b
FUNC_GET_GUID_VER = 0x2C

FUNC_DIST_LIC_APP = 0x30		#手机远程流量授权

FUNC_KEY_UNLOCK	= 0x40
FUNC_DOWNLOAD_OPERATOR = 0x42
FUNC_QUERY_REC_NUM = 0x43
FUNC_QUERY_REC_LEN = 0x44
FUNC_QUERY_REC_CTX = 0x45

#=============    增加   ===================
FUNC_CLEAR_REC_ALL = 0x46	# 清除所有操作记录
FUNC_ADD_REC_START = 0x47	# 开始增加操作记录
FUNC_ADD_REC_CTX = 0x48	# 增加一条操作记录
FUNC_ADD_REC_END = 0x49	# 结束增加操作记录
#===========================================

STRUCT_RESPONCE = 0
STRUCT_MESSAGE = 1
STRUCT_TIMSTAMP = 2
STRUCT_OVERPROCESS = 3
STRUCT_OVERTIME = 4
STRUCT_ISRUNNING = 5

E40FRAMEHEAD = [0xA5, 0x5A, 0xA5, 0x5A]

commanddict = {
    CMD_LMO:"CMD_LMO", # 链路维护命令\
    CMD_KMG:"CMD_KMG", # 钥匙管理机相关命令集\
    CMD_GP:"CMD_GP",  #链路维护命令\
    CMD_GP_JS:"CMD_GP_JS",  #链路维护命令\
    CMD_GP_UP:"CMD_GP_UP", #链路维护命令\
    CMD_GP_DOWN:"CMD_GP_DOWN"  #链路维护命令\
}

CMDDIR_ASK = 0
CMDDIR_REQUEST = 1

cmddirectdict = {
   CMDDIR_ASK:"CMDDIR_ASK",           \
   CMDDIR_REQUEST:"CMDDIR_REQUEST"
}

functiondict = {
    FUNC_LOGIN:"FUNC_LOGIN",\
    FUNC_HB:"FUNC_HB",\
    FUNC_TIMING:"FUNC_TIMING",\

    FUNC_KEY_STATE:"FUNC_KEY_STATE",\
    FUNC_QUERY_STATE:"FUNC_QUERY_STATE",\
    FUNC_UPLOAD_STATE:"FUNC_UPLOAD_STATE",\
    FUNC_QUERY_REC:"FUNC_QUERY_REC",\
    FUNC_UPLOAD_REC:"FUNC_UPLOAD_REC",\

    FUNC_DOWNLOAD_TASKINFO:"FUNC_DOWNLOAD_TASKINFO",\
    FUNC_DOWNLOAD_TASK_LEN:"FUNC_DOWNLOAD_TASK_LEN",\
    FUNC_DOWNLOAD_TASK_CTX:"FUNC_DOWNLOAD_TASK_CTX",\
    FUNC_DELETE_TASK:"FUNC_DELETE_TASK",\

    FUNC_DOWNLOAD_USERINFO_LEN:"FUNC_DOWNLOAD_USERINFO_LEN",\
    FUNC_DOWNLOAD_USERINFO_CTX:"FUNC_DOWNLOAD_USERINFO_CTX",\

    FUNC_UPLOAD_KEYSINFO_LEN:"FUNC_UPLOAD_KEYSINFO_LEN",\
    FUNC_UPLOAD_KEYSINFO_CTX:"FUNC_UPLOAD_KEYSINFO_CTX",\
    FUNC_DOWNLOAD_KEYSINFO_LEN:"FUNC_DOWNLOAD_KEYSINFO_LEN",\
    FUNC_DOWNLOAD_KEYSINFO_CTX:"FUNC_DOWNLOAD_KEYSINFO_CTX",\

    FUNC_UPGRADE_LEN:"FUNC_UPGRADE_LEN",\
    FUNC_UPGRADE_CTX:"FUNC_UPGRADE_CTX",\
    FUNC_FONT_LEN:"FUNC_FONT_LEN",\
    FUNC_FONT_CTX:"FUNC_FONT_CTX",\
    FUNC_UPLOAD_SYS_CFG_LEN:"FUNC_UPLOAD_SYS_CFG_LEN",\
    FUNC_UPLOAD_SYS_CFG_CTX:"FUNC_UPLOAD_SYS_CFG_CTX",\
    FUNC_SET_SYS_CFG_LEN:"FUNC_SET_SYS_CFG_LEN",\
    FUNC_SET_SYS_CFG_CTX:"FUNC_SET_SYS_CFG_CTX",\
    FUNC_UPLOAD_USER_CFG_LEN:"FUNC_UPLOAD_USER_CFG_LEN",\
    FUNC_UPLOAD_USER_CFG_CTX:"FUNC_UPLOAD_USER_CFG_CTX",\
    FUNC_SET_USER_CFG_LEN:"FUNC_SET_USER_CFG_LEN",\
    FUNC_SET_USER_CFG_CTX:"FUNC_SET_USER_CFG_CTX",\
    FUNC_UPLOAD_KEY_CFG_LEN:"FUNC_UPLOAD_KEY_CFG_LEN",\
    FUNC_UPLOAD_KEY_CFG_CTX:"FUNC_UPLOAD_KEY_CFG_CTX",\
    FUNC_SET_KEY_CFG_LEN:"FUNC_SET_KEY_CFG_LEN",\
    FUNC_SET_KEY_CFG_CTX:"FUNC_SET_KEY_CFG_CTX",\
    FUNC_UPLOAD_UNLOCK_CFG_LEN:"FUNC_UPLOAD_UNLOCK_CFG_LEN",\
    FUNC_UPLOAD_UNLOCK_CFG_CTX:"FUNC_UPLOAD_UNLOCK_CFG_CTX",\
    FUNC_SET_UNLOCK_CFG_LEN:"FUNC_SET_UNLOCK_CFG_LEN",\
    FUNC_SET_UNLOCK_CFG_CTX:"FUNC_SET_UNLOCK_CFG_CTX",\

    FUNC_REBOOT:"FUNC_REBOOT",\
    FUNC_AUTO_SET_KEY:"FUNC_AUTO_SET_KEY",\
    FUNC_OPEN_DOOR:"FUNC_OPEN_DOOR",\
    FUNC_FORMAT_NANDFLASH:"FUNC_FORMAT_NANDFLASH",\
    FUNC_UPLOAD_RFID:"FUNC_UPLOAD_RFID",\
    FUNC_GET_BUILDTIME:"FUNC_GET_BUILDTIME",\
    FUNC_GET_GUID_VER:"FUNC_GET_GUID_VER",\

    FUNC_DIST_LIC_APP:"FUNC_DIST_LIC_APP", #手机远程流量授权\

    FUNC_KEY_UNLOCK:"FUNC_KEY_UNLOCK",\
    FUNC_DOWNLOAD_OPERATOR:"FUNC_DOWNLOAD_OPERATOR",\
    FUNC_QUERY_REC_NUM:"FUNC_QUERY_REC_NUM",\
    FUNC_QUERY_REC_LEN:"FUNC_QUERY_REC_LEN",\
    FUNC_QUERY_REC_CTX:"FUNC_QUERY_REC_CTX",\

    FUNC_CLEAR_REC_ALL:"FUNC_CLEAR_REC_ALL",	# 清除所有操作记录\
    FUNC_ADD_REC_START:"FUNC_ADD_REC_START",	# 开始增加操作记录\
    FUNC_ADD_REC_CTX:"FUNC_ADD_REC_CTX",	# 增加一条操作记录\
    FUNC_ADD_REC_END:"FUNC_ADD_REC_END",	# 结束增加操作记录\
}

infunctiondict = {
    "FUNC_LOGIN":0x00, # 注册\
    "FUNC_HB":0x01, # 心跳检测\
    "FUNC_TIMING":0x02, # 校时\

    "FUNC_KEY_STATE":0x01, # 管理机发送单个钥匙状态\
    "FUNC_QUERY_STATE":0x02,\
    "FUNC_UPLOAD_STATE":0x03,\
    "FUNC_QUERY_REC":0x04,\
    "FUNC_UPLOAD_REC":0x05,\

    "FUNC_DOWNLOAD_TASKINFO":0x07,\
    "FUNC_DOWNLOAD_TASK_LEN":0x08,\
    "FUNC_DOWNLOAD_TASK_CTX":0x09,\
    "FUNC_DELETE_TASK":0x0A,\

    "FUNC_DOWNLOAD_USERINFO_LEN":0x0B,\
    "FUNC_DOWNLOAD_USERINFO_CTX":0x0C,\

    "FUNC_UPLOAD_KEYSINFO_LEN":0x0D,\
    "FUNC_UPLOAD_KEYSINFO_CTX":0x0E,\
    "FUNC_DOWNLOAD_KEYSINFO_LEN":0x0F,\
    "FUNC_DOWNLOAD_KEYSINFO_CTX":0x10,\

    "FUNC_UPGRADE_LEN":0x11,\
    "FUNC_UPGRADE_CTX":0x12,\
    "FUNC_FONT_LEN":0x13,\
    "FUNC_FONT_CTX":0x14,\
    "FUNC_UPLOAD_SYS_CFG_LEN":0x15,\
    "FUNC_UPLOAD_SYS_CFG_CTX":0x16,\
    "FUNC_SET_SYS_CFG_LEN":0x1d,\
    "FUNC_SET_SYS_CFG_CTX":0x1e,\
    "FUNC_UPLOAD_USER_CFG_LEN":0x17,\
    "FUNC_UPLOAD_USER_CFG_CTX":0x18,\
    "FUNC_SET_USER_CFG_LEN":0x1f,\
    "FUNC_SET_USER_CFG_CTX":0x20,\
    "FUNC_UPLOAD_KEY_CFG_LEN":0x19,\
    "FUNC_UPLOAD_KEY_CFG_CTX":0x1a,\
    "FUNC_SET_KEY_CFG_LEN":0x21,\
    "FUNC_SET_KEY_CFG_CTX":0x22,\
    "FUNC_UPLOAD_UNLOCK_CFG_LEN":0x1b,\
    "FUNC_UPLOAD_UNLOCK_CFG_CTX":0x1c,\
    "FUNC_SET_UNLOCK_CFG_LEN":0x23,\
    "FUNC_SET_UNLOCK_CFG_CTX":0x24,\

    "FUNC_REBOOT":0x25,\
    "FUNC_AUTO_SET_KEY":0x26,\
    "FUNC_OPEN_DOOR":0x27,\
    "FUNC_FORMAT_NANDFLASH":0x28,\
    "FUNC_UPLOAD_RFID":0x29,\
    "FUNC_GET_BUILDTIME":0x2b,\
    "FUNC_GET_GUID_VER":0x2C,\

    "FUNC_DIST_LIC_APP":0x30,		#手机远程流量授权\

    "FUNC_KEY_UNLOCK":0x40,\
    "FUNC_DOWNLOAD_OPERATOR":0x42,\
    "FUNC_QUERY_REC_NUM":0x43,\
    "FUNC_QUERY_REC_LEN":0x44,\
    "FUNC_QUERY_REC_CTX":0x45,\
    "FUNC_CLEAR_REC_ALL":0x46,# 清除所有操作记录\
    "FUNC_ADD_REC_START":0x47,	# 开始增加操作记录\
    "FUNC_ADD_REC_CTX":0x48,	# 增加一条操作记录\
    "FUNC_ADD_REC_END":0x49,	# 结束增加操作记录\
}

def swap_bytes(word_val):
    """swap lsb and msb of a word"""
    msb = (word_val >> 8) & 0xFF
    lsb = word_val & 0xFF
    return (lsb << 8) + msb

def calculate_crc(data):
    """Calculate the CRC16 of a datagram"""
    CRC16table = (
        0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
        0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
        0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
        0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
        0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
        0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
        0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
        0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
        0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
        0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
        0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
        0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
        0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
        0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
        0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
        0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
        0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
        0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
        0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
        0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
        0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
        0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
        0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
        0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
        0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
        0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
        0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
        0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
        0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
        0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
        0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
        0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
    )
    crc = 0xFFFF
    for c in data:
        crc = (crc >> 8) ^ CRC16table[(c ^ crc) & 0xFF]
    return swap_bytes(crc)

def proc_request_loginon(parameter):
    try:
        deviceid = parameter.get('deviceid')
        tempdata = [0x00, 0x04, 0x05, 0x80, \
                            0x00, 0x00, 0x00, 0x00, 0x6E, 0x6E, 0x80, 0x00, deviceid, 0x00]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        machineid=parameter.get('machineid')
        onlinekeymachine[machineid]['address'] = deviceid
        responce = onlinekeymachine.get(machineid).get('socket')
       #responce.send(bytes(tempdata))
        envdata.send_proclist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
        #for taskpool in envdata.pre_commandlist:
        #    if taskpool[STRUCT_TIMSTAMP] == parameter.get('timestamp'):
        #        envdata.pre_commandlist.remove(taskpool)
        return 'SUCCESS'
    except (IOError, Exception) as v:
        return 'LINKERROR'

def proc_refresh_key(parameter):
    if parameter.__contains__('machineid'):
        machineid = parameter.get('machineid')
        deviceid = onlinekeymachine[machineid].get('address')
        tempdata = tempdata = [0x00, 0x02, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x26]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        try:
            responce = onlinekeymachine.get(machineid).get('socket')
            responce.send(bytes(tempdata))
            return 'SUCCESS'
        except IOError as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_send_time(parameter):
    if parameter.__contains__('machineid'):
        try:
            machineid = parameter.get('machineid')
            deviceid = onlinekeymachine[machineid].get('address')
            curtime = time.struct_time(time.localtime())
            year = curtime.tm_year
            month = curtime.tm_mon
            day = curtime.tm_mday
            hour= curtime.tm_hour
            minute = curtime.tm_min
            second = curtime.tm_sec
            tempdata = [0x00, 0x09, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x00, 0x02,\
                                (year>>8) & 0xFF, year & 0xFF, month, day, hour, minute, second]
            tempcrc = calculate_crc(tempdata)
            tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
            responce = onlinekeymachine.get(machineid).get('socket')
            #responce.send(bytes(tempdata))
            envdata.send_proclist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            return 'SUCCESS'
        except (IOError, Exception) as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_reset_machine(parameter):
    if parameter.__contains__('machineid'):
        machineid = parameter.get('machineid')
        deviceid = onlinekeymachine[machineid].get('address')
        tempdata = [0x00, 0x02, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x25]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        try:
            responce = onlinekeymachine.get(machineid).get('socket')
            responce.send(bytes(tempdata))
            return 'SUCCESS'
        except IOError as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_open_mechine(parameter):
    if parameter.__contains__('machineid'):
        machineid = parameter.get('machineid')
        deviceid = onlinekeymachine[machineid].get('address')
        tempdata = [0x00, 0x02, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x27]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        try:
            responce = onlinekeymachine.get(machineid).get('socket')
            #responce.send(bytes(tempdata))
            envdata.send_proclist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            return 'SUCCESS'
        except IOError as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_unlock_allkey(parameter):
    if parameter.__contains__('machineid'):
        machineid = parameter.get('machineid')
        deviceid = onlinekeymachine[machineid].get('address')
        tempdata = [0x00, 0x02, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x00, 0x11]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        try:
            responce = onlinekeymachine.get(machineid).get('socket')
            #responce.send(bytes(tempdata))
            envdata.send_proclist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            return 'SUCCESS'
        except IOError as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_break_heart(parameter):
    if parameter.__contains__('machineid'):
        machineid = parameter.get('machineid')
        deviceid = onlinekeymachine[machineid].get('address')
        tempdata = [0x00, 0x02, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x00, 0x01]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        try:
            responce = onlinekeymachine.get(machineid).get('socket')
            #responce.send(bytes(tempdata))
            envdata.send_proclist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            return 'SUCCESS'
        except IOError as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_allkey_status(parameter):
    if parameter.__contains__('machineid'):
        machineid = parameter.get('machineid')
        deviceid = onlinekeymachine[machineid].get('address')
        tempdata = [0x00, 0x02, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x0D]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        try:
            responce = onlinekeymachine.get(machineid).get('socket')
            #responce.send(bytes(tempdata))
            envdata.send_proclist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            return 'SUCCESS'
        except IOError as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_updata_font(parameter):
    if parameter.__contains__('machineid') and parameter.__contains__('fontdata')\
            and parameter.__contains__('fontbcc'):
        machineid = parameter.get('machineid')
        deviceid = onlinekeymachine[machineid].get('address')
        fontdata = parameter.get("fontdata")
        tempfont = fontdata.data
        tempsize = len(tempfont)
        tempbcc = parameter.get("fontbcc")
        templen = int(tempsize/900 + 1)
        tempdata = [0x00, 0x09, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x13, templen>>8,\
                                templen&0xFF, (tempsize>>24)&0xFF,(tempsize>>16)&0xFF,(tempsize>>8)&0xFF,tempsize&0xFF,tempbcc]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        try:
            responce = onlinekeymachine.get(machineid).get('socket')
            #responce.send(bytes(tempdata))
            templist = []
            #envdata.send_proclist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            templist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            for i in range(templen):
                if tempsize > (i*900+899):
                    tempdata = list([(900+6)>>8, (900+6)&0xFF])
                    tempdata += [0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x14, (i+1)>>8, (i+1)&0xFF, 900>>8, 900&0xFF]
                    tempdata += list(tempfont[i*900:(i+1)*900])
                    tempcrc = calculate_crc(tempdata)
                    tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
                    responce = onlinekeymachine.get(machineid).get('socket')
                    templist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
                else:
                    tempdata = list([((tempsize-i*900)+6)>>8, ((tempsize-i*900)+6)&0xFF])
                    tempdata += [0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x14, (i+1)>>8, (i+1)&0xFF, (tempsize-i*900)>>8, (tempsize-i*900)&0xFF]
                    tempdata += list(tempfont[i*900:tempsize])
                    tempcrc = calculate_crc(tempdata)
                    tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
                    responce = onlinekeymachine.get(machineid).get('socket')
                    templist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            envdata.send_proclist.append(templist)
            return 'SUCCESS'
        except IOError as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_updata_prog(parameter):
    if parameter.__contains__('machineid') and parameter.__contains__('progdata')\
            and parameter.__contains__('progbcc'):
        machineid = parameter.get('machineid')
        deviceid = onlinekeymachine[machineid].get('address')
        progdata = parameter.get("progdata")
        tempprog = progdata.data
        tempsize = len(tempprog)
        tempbcc = parameter.get("progbcc")
        templen = int(tempsize/900 + 1)
        tempdata = [0x00, 0x09, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x11, templen>>8,\
                                templen&0xFF, (tempsize>>24)&0xFF,(tempsize>>16)&0xFF,(tempsize>>8)&0xFF,tempsize&0xFF,tempbcc]
        tempcrc = calculate_crc(tempdata)
        tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
        try:
            responce = onlinekeymachine.get(machineid).get('socket')
            #responce.send(bytes(tempdata))
            templist = []
            #envdata.send_proclist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            templist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            for i in range(templen):
                if tempsize > (i*900+899):
                    tempdata = list([(900+6)>>8, (900+6)&0xFF])
                    tempdata += [0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x12, (i+1)>>8, (i+1)&0xFF, 900>>8, 900&0xFF]
                    tempdata += list(tempprog[i*900:(i+1)*900])
                    tempcrc = calculate_crc(tempdata)
                    tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
                    responce = onlinekeymachine.get(machineid).get('socket')
                    templist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
                else:
                    tempdata = list([((tempsize-i*900)+6)>>8, ((tempsize-i*900)+6)&0xFF])
                    tempdata += [0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x14, (i+1)>>8, (i+1)&0xFF, (tempsize-i*900)>>8, (tempsize-i*900)&0xFF]
                    tempdata += list(tempprog[i*900:tempsize])
                    tempcrc = calculate_crc(tempdata)
                    tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
                    responce = onlinekeymachine.get(machineid).get('socket')
                    templist.append(dict({"responce":responce, "tempdata":tempdata, "machineid":machineid, "timestamp":parameter.get('timestamp')}))
            envdata.send_proclist.append(templist)
            return 'SUCCESS'
        except IOError as v:
            return 'LINKERROR'
    else:
        return 'ERROR'

def proc_commandmax(parameter):
    return parameter

commandentry = dict(REQUEST_LOGINON=proc_request_loginon,\
                    REFRESH_KEY=proc_refresh_key,\
                    RESET_MACHINE=proc_reset_machine,\
                    SEND_TIME=proc_send_time,\
                    OPEN_MECHINE=proc_open_mechine,\
                    UNLOCK_ALLKEY=proc_unlock_allkey,\
                    BREAK_HEART=proc_break_heart,\
                    ALLKEY_STATUS=proc_allkey_status,\
                    UPDATE_FONT=proc_updata_font,\
                    UPDATE_PROG=proc_updata_prog,\
                    COMMANDMAX=proc_commandmax)

def download_from_control(data):
    if data.__contains__('cmd'):
        cmd = data.get('cmd')
    else:
        result = {'error': 'Fault error in command'}
        return result
    #解析指令并执行之
    if cmd in commandentry.keys():
        return commandentry[cmd](data)
    else:
        result = {'error': 'Fault error in command'}
        return result


def upload_to_control():
    tempdata = list()
    for item in upload_pool:
        #item.update(dict())
        print(item, type(item))
        tempdata.append(item)
    upload_pool.clear()
    return tempdata

def beginrpcserver():
    with SimpleXMLRPCServer(SEVER_NAME) as server:
        server.register_function(upload_to_control)
        server.register_function(download_from_control)
        #server.register_function(initial)
        #server.register_instance(service, allow_dotted_names=True)
        server.register_multicall_functions()
        print('Serving XML-RPC on localhost port 20001')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

class E40proctol():
    def __init__(self, data):
        self.contentLength = (data[0]<< 8) + data[1]
        self.proctolType = data[2]
        self.controlType = data[3]
        self.sourceAddress = (data[4]<< 8) + data[5]
        self.distineseAddress = (data[6]<< 8) + data[7]
        self.sourceType = data[8]
        self.distineseType = data[9]
        self.commond = data[10]
        self.function = data[11]
        self.data = data[12: len(data)]

    def __getattr__(self, item):
        return item

def response_40(taskdata):
        if taskdata[STRUCT_MESSAGE].commond == CMD_LMO:
            if taskdata[STRUCT_MESSAGE].function  == FUNC_LOGIN:
                tempdict = dict()
                tempdata = taskdata[STRUCT_MESSAGE].data
                templen = (tempdata[4] << 8) + tempdata[5]
                temparray = tempdata[6:(6+templen)]
                machineid = hashlib.new('md5', temparray).hexdigest()
                tempdict['machineid'] = machineid
                tempdict['socket'] = taskdata[STRUCT_RESPONCE]
                tempdict['address'] = 0
                tempdict['station'] = 0
                onlinekeymachine[machineid] = tempdict
                upload_pool.append({'function': 'CMD_LOGINON',\
                                        'machineid': machineid,\
                                        'timestamp': taskdata[STRUCT_TIMSTAMP],\
                                        })

def response_80(taskdata):            #应答帧带数据
    for item in envdata.waitresult_list:
        command = item.get('tempdata')[14] | 0x80
        function = item.get('tempdata')[15]
        if command == taskdata[STRUCT_MESSAGE].commond and function== taskdata[STRUCT_MESSAGE].function:
            command2 = taskdata[STRUCT_MESSAGE].commond & 0x0f
            function2 = taskdata[STRUCT_MESSAGE].function
            if command2 == 0x0a and function2 == 0x0d:
                num = taskdata[STRUCT_MESSAGE].data[1]                  #取出钥匙信息帧总数
                deviceid = item.get('tempdata')[10]
                envdata.waitresult_list.remove(item)
                templist = []
                for count in range(num):
                    tempdata = [0x00, 0x04, 0x05, 0x40, \
                                0x00, 0x00, deviceid, 0x00, 0x6E, 0x6E, 0x0A, 0x0E, 0x00, count+1]
                    tempcrc = calculate_crc(tempdata)
                    tempdata = E40FRAMEHEAD + tempdata + [(tempcrc & 0xFF), ((tempcrc >> 8) & 0xFF)]
                    item['tempdata'] = tempdata
                    templist.append(item)
                envdata.send_proclist.append(templist)
                break
            if command2 == 0x0a and function2 == 0x0e:
                envdata.waitresult_list.remove(item)
                upload_pool.append({'function': 'CMD_LOGINON',\
                                        'machineid': machineid,\
                                        'timestamp': taskdata[STRUCT_TIMSTAMP],\
                                        })
                break
        else:
            pass

def response_81(taskdata):            #ACK,NACK帧
    for item in envdata.waitresult_list:
        command = item.get('tempdata')[14] | 0x80
        function = item.get('tempdata')[15]
        command2 = taskdata[STRUCT_MESSAGE].commond
        function2 = taskdata[STRUCT_MESSAGE].function
        if command == taskdata[STRUCT_MESSAGE].commond and function== taskdata[STRUCT_MESSAGE].function:
           envdata.waitresult_list.remove(item)

def receive_proc():
    try:
        if (len(envdata.receive_proclist) > 0):
            currentmsg = envdata.receive_proclist[0]
            message = E40proctol(currentmsg[1])
            responce = currentmsg[0]
            timstamp = currentmsg[2]
            overtime = time.time() + 20
            overprocess = 3
            isrunning = 0
            envdata.pre_commandlist.append([responce, message, timstamp,overprocess, overtime, isrunning])
            envdata.receive_proclist.remove(currentmsg)
            if len(envdata.pre_commandlist) > 0:
                for taskpool in envdata.pre_commandlist:
                    if taskpool[STRUCT_OVERTIME] < time.time():
                        if taskpool[STRUCT_OVERPROCESS] > 0:
                            #print(taskpool[STRUCT_TIMSTAMP], '    ', taskpool[STRUCT_OVERTIME])
                            taskpool[STRUCT_OVERTIME] = time.time() + 20
                            taskpool[STRUCT_OVERPROCESS] -= 1
                            taskpool[STRUCT_ISRUNNING] = 0
                        else:
                            print('delete ', taskpool[STRUCT_TIMSTAMP])
                            envdata.pre_commandlist.remove(taskpool)
                    else:
                        if taskpool[STRUCT_ISRUNNING] == 0:
                        #mainproc
                            if taskpool[STRUCT_MESSAGE].controlType & 0xFF == CTRL_WORD_SEND:   # 0x40
                                response_40(taskpool)
                                taskpool[STRUCT_ISRUNNING] = 1
                            elif taskpool[STRUCT_MESSAGE].controlType & 0xFF == CTRL_WORD_RESP:   #0x80
                                response_80(taskpool)
                                taskpool[STRUCT_ISRUNNING] = 1
                            elif taskpool[STRUCT_MESSAGE].controlType & 0xFF == CTRL_WORD_ACK:  #0x80
                                response_81(taskpool)
                                taskpool[STRUCT_ISRUNNING] = 1
                            else:
                                envdata.pre_commandlist.remove(taskpool)
    except IOError:
        print("receive_proc error")

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            while True:
                data=self.request.recv(1024)
                if (data[0] == 0xA5) and (data[1] == 0x5A) and (data[2] == 0xA5) and (data[3] == 0x5A):
                    tempdata = data[4: (len(data) - 2)]
                    tempcrc = calculate_crc(tempdata)
                    if((tempcrc >> 8) & 0xFF) == data[-1] and (tempcrc & 0xFF) == data[-2]:
                        envdata.receive_proclist.append([self.request, tempdata, time.time()])
        except Exception as e:
            print(self.client_address,"连接断开")
            envdata.pre_send_proclist.clear()
            envdata.send_proclist.clear()
        finally:
            self.request.close()

    def setup(self):
        print("before handle,连接建立：",self.client_address)

    def finish(self):
        print("finish run  after handle")

def wait_result_proc():
    try:
        if len(envdata.waitresult_list) > 0:
            for task in envdata.waitresult_list:
                if time.time() > task["overtime"]:
                    envdata.waitresult_list.remove(task)
                    for taskpool in envdata.pre_commandlist:
                        if taskpool[STRUCT_TIMSTAMP] == task.get('timestamp'):
                            envdata.pre_commandlist.remove(taskpool)
    except Exception:
        print("wait_result_proc error")

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
                        envdata.running_commandlist.remove(task)
                else:
                    if task.get("isrunned") == False:
                        responce = onlinekeymachine.get(task.get("machineid")).get('socket')
                        #result = task["responce"].send(bytes(task["tempdata"]))
                        result = responce.send(bytes(task["tempdata"]))
                        if result > 0:
                            envdata.running_commandlist.remove(task)
                            task["overtime"] = time.time() + OVERTIME
                            envdata.waitresult_list.append(task)
                            for taskpool in envdata.pre_commandlist:
                                if taskpool[STRUCT_TIMSTAMP] == task.get('timestamp'):
                                    envdata.pre_commandlist.remove(taskpool)
                            break
                        else:
                            task["isrunned"] = True
    except Exception as e:
        print("run_cmd_proc error")

def pre_cmd_proc():
    try:
        if len(envdata.pre_send_proclist) > 0 and len(envdata.running_commandlist) == 0:
            tempdict = envdata.pre_send_proclist.pop(0)
            tempdict["isrunned"] = False
            tempdict["overprocess"]=OVERNUM
            tempdict["overtime"]=time.time()+OVERTIME
            envdata.running_commandlist.append(tempdict)
        else:
            pass
    except Exception:
        print("pre_cmd_proc error")

def checkconnected():
    if len(upload_pool) > 5:
        upload_pool.clear()

def send_cmd_proc():
    if len(envdata.send_proclist) > 0:
        for functionitem in envdata.send_proclist:
            if isinstance(functionitem, dict):
                envdata.pre_send_proclist.append(functionitem)
                envdata.send_proclist.remove(functionitem)
            elif isinstance(functionitem, list):
                if len(envdata.waitresult_list) ==0 and len(envdata.running_commandlist) == 0:
                    subfunctionitem = functionitem[0]
                    functionitem.remove(subfunctionitem)
                    envdata.pre_send_proclist.append(subfunctionitem)
                    if len(functionitem) == 0:
                        envdata.send_proclist.remove(functionitem)
            else:
                envdata.send_proclist.remove(functionitem)

def mainproc():
    while True:
        try:
            checkconnected()
            wait_result_proc()
            run_cmd_proc()
            pre_cmd_proc()
            send_cmd_proc()
            receive_proc()
        except Exception:
            pass

def main():
    server_thread = Thread(target=beginrpcserver)
    server_thread.daemon = True
    server_thread.start()
    envdata.funcproc = threading.Thread(target=mainproc)
    envdata.funcproc.setDaemon(True)
    envdata.funcproc.start()
    server=socketserver.ThreadingTCPServer(('', TCP_PORT),MyTCPHandler)#多线程版
    server.serve_forever()


if __name__ == "__main__":
    main()