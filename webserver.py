# _*_ coding: utf-8 _*_
import xmlrpc.client
from xml.etree import ElementTree as ET

from flask import Flask, url_for, request

from jinja2 import Environment, PackageLoader

from static.python.common import dbconnect, globaldata

app = Flask(__name__)

envdata = globaldata.globel()
envdata.function = 0
envdata.server = ''
envdata.port = 80
envdata.databasename = ''
envdata.function_name = ''
envdata.userlist = []
envdata.functionlist = []

def initial():
    str_xml = open("static/config/user.xml", 'r').read()
    root = ET.XML(str_xml)
    for user in root:
        envdata.userlist.append(user.attrib)
    str_xml = open('static/config/function.xml', 'r').read()
    root = ET.XML(str_xml)
    for func in root:
        envdata.functionlist.append(func.attrib)

@app.route('/')
def hello_world():
    env = Environment(loader=PackageLoader('webserver', 'templates'))
    template = env.get_template('login.html')
    #template.render()
    #env = Environment()
    #template = env.from_string('Hello {{ name }}')
    #return template.render(name = 'Xiaoming')
    return template.render(name = '登录用户', backgroud_pic = url_for('static', filename = 'images/timg.jpeg'), login_pic = url_for('static', filename = 'images/login.png'))
    #return '<h1> hello the world </h1>'

@app.route('/login/<html>', methods=['POST', 'GET'])
def admin_login(html):
    userid = request.values['userid']
    password = request.values['password']
    envdata.user = userid
    envdata.password = password
    for user in envdata.userlist:
        if user['name'] == userid:
            if user['password'] == password:
                tempstr = '<p>功能选择：</p><ul>'
                for func in envdata.functionlist:
                    str = '<li><a href="/choose.html?function=%s">%s</a></li>' % (func['id'], func['title'])
                    tempstr += str
                tempstr += '</ul>'
                env = Environment(loader=PackageLoader('webserver', 'templates'))
                template = env.get_template('choose.html')
                return template.render(top_name = '选择相应的功能',\
                                           name = '选择相应组件' ,\
                                           backgroud_pic = url_for('static',\
                                           filename = 'images/timg.jpeg'), \
                                           choose_leftpage = tempstr)
    env = Environment(loader=PackageLoader('webserver', 'templates'))
    template = env.get_template('login.html')
    return template.render(name = '登录用户', \
                           backgroud_pic = url_for('static', \
                           filename = 'images/timg.jpeg'), \
                           login_pic = url_for('static', \
                           filename = 'images/login.png'))


@app.route('/choose.html', methods=['GET', 'POST'])
def choose_html():
    envdata.function = request.values['function']
    for func in envdata.functionlist:
        if func.get("id") == envdata.function:
            envdata.function_name = func['title']
            envdata.server = func['addr']
            envdata.port = func['port']
    rpcserver = "http://%s:%s" % (envdata.server, envdata.port)
    server = xmlrpc.client.ServerProxy(rpcserver)
    try:
        returnstr = server.setup(envdata.function, envdata.function_name)
        return returnstr
    except xmlrpc.client.Error as v:
        return("ERROR", v)

@app.route('/running/<html>' ,methods=['GET', 'POST'])
def running_html(html):
    if html == "initial.html":
        rpcserver = "http://%s:%s" % (envdata.server, envdata.port)
        server = xmlrpc.client.ServerProxy(rpcserver)
        try:
            tempdict = dict()
            for value in request.values:
                tempdict.update({value: request.values[value]})
            returnstr = server.initial(tempdict)
            return returnstr
        except xmlrpc.client.Error as v:
            return("ERROR", v)
    elif html == "function.html":
        rpcserver = "http://%s:%s" % (envdata.server, envdata.port)
        server = xmlrpc.client.ServerProxy(rpcserver)
        try:
            tempdict = dict()
            for value in request.values:
                tempdict.update({value: request.values[value]})
            returnstr = server.function(tempdict)
            return returnstr
        except xmlrpc.client.Error as v:
            return("ERROR", v)
    else:
        return '<h1> hello the default </h1>'

def test():
    str_xml = open('static/config/function.xml', 'r').read()
    root = ET.XML(str_xml)
    funclist=[]
    for user in root:
        funclist.append(user.attrib)
    print(funclist)


if __name__ == "__main__":
    #test()
    initial()
    app.run(port=3011)