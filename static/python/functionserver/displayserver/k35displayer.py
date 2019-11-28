from xmlrpc.server import SimpleXMLRPCServer
import sys
import threading
import xmlrpc.client
from jinja2 import Environment, PackageLoader
from static.python.common import globaldata
from xml.etree import ElementTree as ET
import time

SERVER_NAME = ('127.0.0.1', 50001)

HEAD = 0
TOP = 1
CONTENTPAGE = 2
BOTPAGE = 3
SCRIPTHEAD = 4
SCRIPTBODY = 5

basedir = "static/assets/test"      #最简界面用的是这个路径下的配置

def function_x(tempdict):
    templist = []
    return templist

def initial(tempdict):
    templist = list(["","","","","",""])
    tempdict["function"] = "CMD_FRESHDISPLAY"
    tempdict["timestamp"] = time.time()
    templist[CONTENTPAGE] = '<div id="left"><form action="running.html" method="get">'
    for k,v in tempdict.items():
        templist[CONTENTPAGE] += '<input type="text" id="freshmeter" name="%s" value="%s" hidden="hidden">'%(k,v)
    templist[CONTENTPAGE] += '<input type="submit" class="hidden" hidden="hidden"></form>'
    templist[BOTPAGE] = ''
    templist[SCRIPTHEAD] = 'setInterval(function(){var tempdata = {};$("input#freshmeter").each(function(){tempdata[$(this).attr("name")] = $(this).attr("value");});$.post("/ajax",tempdata,function(data, status){if(data == "needfresh"){$("input.hidden").click();}});}, 4000);'
    #templist[SCRIPTHEAD] = 'setInterval(function(){'
    #templist[SCRIPTHEAD] += '$("input.hidden").click();'
    #templist[SCRIPTHEAD] += '$.get("/ajax",function(data,status){'
    #templist[SCRIPTHEAD] += 'alert("数据: " + data + "\n状态: " + status);'
    #templist[SCRIPTHEAD] += '});'
    #templist[SCRIPTHEAD] += '},2000);'
    templist[SCRIPTBODY] = ''
    templist[HEAD]='<meta charset="utf-8">\
                    <link href="%s/css/common.css" rel="stylesheet" type="text/css" />\
                    <script src="%s/js/jquery-3.4.1.min.js" type="text/javascript"></script>\
                    <title>%s</title>'%(basedir, basedir, '采用的是最简界面')
    templist[TOP]='<p class="title"> 选择相应钥匙管理机 </p>'
    return templist

def beginrpc():
    with SimpleXMLRPCServer(SERVER_NAME) as server:
        server.register_function(initial, 'initial')
        server.register_function(function_x, 'function')
        server.register_multicall_functions()
        print('Serving XML-RPC on localhost port 50001')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

def main():
    beginrpc()

if __name__ == "__main__":
    main()