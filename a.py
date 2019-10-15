from xml.etree import ElementTree as ET
import threading
import xmlrpc.client

def test():
    str_xml = open("static/config/user.xml", 'r').read()
    root = ET.XML(str_xml)
    userlist=[]
    for user in root:
        userlist.append(user.attrib)
    print(userlist)

def timerfunc():
    rpcserver = "http://%s:%s" % ("127.0.0.1", 50001)
    s = xmlrpc.client.ServerProxy(rpcserver)
    # print s.pow(2, 3)
    print(s.div(5, 2))
    t = threading.Timer(1, timerfunc)
    t.start()

if __name__ == "__main__":
    timerfunc()