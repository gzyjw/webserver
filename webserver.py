# _*_ coding: utf-8 _*_
import xmlrpc.client
import time
from xml.etree import ElementTree as ET

from flask import Flask, url_for, request, redirect

from jinja2 import Environment, PackageLoader

from static.python.common import globaldata

from static.python.viewport import k35aview

import json

app = Flask(__name__)

envdata = globaldata.globel()
envdata.userlist = []
envdata.functionlist = []


def initial():
    envdata.userlist.clear()
    envdata.functionlist.clear()
    str_xml = open("static/config/user.xml", 'r').read()
    root = ET.XML(str_xml)
    for user in root:
        envdata.userlist.append(user.attrib)
    str_xml = open('static/config/function.xml', 'r').read()
    root = ET.XML(str_xml)
    for func in root:
        envdata.functionlist.append(func.attrib)


def getfunc(tempdict):
    for funcitem in envdata.functionlist:
        if funcitem.get("id") == tempdict.get('funclist'):
            functionserverinfo = (funcitem.get("addr"), int(funcitem.get("port")))
            rpcserver = "http://%s:%s" % functionserverinfo
            server = xmlrpc.client.ServerProxy(rpcserver)
    return server


@app.route('/')
def login():
    initial()
    env = Environment(loader=PackageLoader('webserver', 'templates'))
    template = env.get_template('login.html')
    return template.render(titlename='多功能远程调试工具')


@app.route('/administor.htm', methods=['POST', 'GET'])
def admin_login():
    tempdict = dict()
    for k, v in request.values.items():
        tempdict[k] = v
    tempstr = '<p class="funcselect">功能选择：</p><ul>'
    for func in envdata.functionlist:
        str = '<li class="funclist"><a href="/choose.html?' + \
              'functionUser=%s&functionPassword=%s&funclist=%s">%s</a></li>' \
              % (tempdict["functionUser"], tempdict["functionPassword"], func['id'], func['title'])
        tempstr += str
        tempstr += '</ul>'
        env = Environment(loader=PackageLoader('webserver', 'templates'))
        template = env.get_template('choose.html')
    return template.render(top_name='选择相应的功能', \
                           name='选择相应组件', \
                           backgroud_pic=url_for('static', \
                                                 filename='images/timg.jpeg'), \
                           choose_leftpage=tempstr)


@app.route('/choose.html', methods=['GET', 'POST'])
def choose_html():
    tempdict = dict()
    for k, v in request.values.items():
        tempdict[k] = v
    functionserver = getfunc(tempdict)
    try:
        returndict = functionserver.setup()
        tempstr = '<form method="get" action="/setup.html">'
        for k, v in tempdict.items():
            tempstr += '<input type="hidden" name="%s" value="%s">' % (k, v)
        for k, v in returndict["index"].items():
            tempstr = tempstr + '<div><p class="funcselect">%s</p>' % v
            for item in returndict[k]:
                tempstr = tempstr + '<li class="funclist">' + \
                          '<input type="radio" name=%s id=%s-%s value=%s><label for=%s-%s>%s</label>' \
                          % (k, item["commit"], item["id"], item["id"], item["commit"], item["id"],
                             item["commit"]) + '</li>'
            tempstr = tempstr + "</div>"
        env = Environment(loader=PackageLoader('webserver', 'templates'))
        template = env.get_template('choose.html')
        return template.render(top_name='选择相应组件', \
                               name='选择相应组件', \
                               choose_leftpage=tempstr,
                               choose_botpage='<p><input id="submit" type="submit" value="确定提交"><p></form>')
    except xmlrpc.client.Error as v:
        return ("ERROR", v)


@app.route('/setup.html', methods=['GET', 'POST'])
def setup_html():
    try:
        tempdict = dict()
        for k, v in request.values.items():
            tempdict[k] = v
        functionserver = getfunc(tempdict)
        returnstr = functionserver.initial(tempdict)
        return redirect(returnstr)
    except xmlrpc.client.Error as v:
        return ("ERROR", v)


@app.route('/running.html', methods=['GET', 'POST'])
def running_html():
    tempdict = dict()
    for k, v in request.values.items():
        tempdict[k] = v
    functionserver = getfunc(tempdict)
    try:
        returndict = functionserver.function(tempdict)
        if returndict['returnresult'] == "donotchange":
            return
        elif returndict['returnresult'] == "freshpage":
            returnlist = returndict["data"]
            env = Environment(loader=PackageLoader('webserver', 'templates'))
            template = env.get_template('running.html')
            return template.render(run_head=returnlist[0], \
                                   run_top=returnlist[1], \
                                   run_contentpage=returnlist[2], \
                                   run_botpage=returnlist[3], \
                                   scriptstrhead=returnlist[4], \
                                   scriptstrbody=returnlist[5])
        else:
            pass
    except xmlrpc.client.Error as v:
        return ("ERROR", v)

@app.route('/ajax', methods=['GET', 'POST'])
def ajax_post():
    try:
        tempdict = dict()
        for k, v in request.values.items():
            tempdict[k] = v
        functionserver = getfunc(tempdict)
        returndict = functionserver.function(tempdict)
        if returndict["returnresult"] == "donotchange":
            return 'noneedfresh'
        else:
            return 'needfresh'
    except Exception as e:
        return 'noneedfresh'
    return 'noneedfresh'



@app.route('/initial.html', methods=['GET', 'POST'])
def initial_html():
    tempdict = dict()
    for k, v in request.values.items():
        tempdict[k] = v
    rpcserver = "http://%s:%s" % (tempdict["functionServer"], tempdict["functionPort"])
    server = xmlrpc.client.ServerProxy(rpcserver)
    try:
        tempdict = dict()
        for value in request.values:
            tempdict.update({value: request.values[value]})
        returndict = server.initial(tempdict)
        tempstr = '<form method="get" action="/begin.html">'
        for k, v in tempdict.items():
            tempstr += '<input type="hidden" name="%s" value="%s">' % (k, v)
        for k, v in returndict["index"].items():
            tempstr = tempstr + '<div><p class="funcselect">%s</p>' % v
            if k == "onlinelist":
                for item in returndict[k]:
                    tempstr = tempstr + '<li class="funclist">' + \
                              '<input type="radio" name=%s id=%s-%s value=%s><label for=%s-%s>%s</label>' \
                              % ("machineid", item["commit"], item["id"], item["id"], item["commit"], item["id"],
                                 item["commit"]) + '</li>'
            else:
                for item in returndict[k]:
                    tempstr = tempstr + '<li class="funclist">' + \
                              '<p>%s</p>' % item["commit"] \
                              + '</li>'

            tempstr = tempstr + "</div>"
        env = Environment(loader=PackageLoader('webserver', 'templates'))
        template = env.get_template('choose.html')
        return template.render(top_name='选择相应设备', \
                               name='选择相应设备', \
                               choose_leftpage=tempstr,
                               choose_botpage='<p><input id="submit" type="submit" value="确定提交"><p></form>')
    except xmlrpc.client.Error as v:
        return ("ERROR", v)


beginviewentry = {"k35aremotedebug": k35aview.beginview}


@app.route('/begin.html', methods=['GET', 'POST'])
def begin_html():
    tempdict = dict()
    for k, v in request.values.items():
        tempdict[k] = v
    rpcserver = "http://%s:%s" % (tempdict["functionServer"], tempdict["functionPort"])
    server = xmlrpc.client.ServerProxy(rpcserver)
    try:
        returndict = server.begin(tempdict)
        returndict = beginviewentry[returndict["functionName"]](returndict)
        env = Environment(loader=PackageLoader('webserver', 'templates'))
        template = env.get_template('running.html')
        return template.render(top_name='选择相应功能', \
                               name='选择相应设备', \
                               run_contentpage=returndict[0], \
                               run_botpage=returndict[1], \
                               scriptstrhead=returndict[2], \
                               scriptstrbody=returndict[3])
    except xmlrpc.client.Error as v:
        return ("ERROR", v)


runnningviewentry = {"k35aremotedebug": k35aview.runningview}



def test():
    str_xml = open('static/config/function.xml', 'r').read()
    root = ET.XML(str_xml)
    funclist = []
    for user in root:
        funclist.append(user.attrib)
    print(funclist)


if __name__ == "__main__":
    # test()
    initial()
    app.run(host='0.0.0.0', port=3011)
