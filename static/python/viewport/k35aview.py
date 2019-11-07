# _*_ coding: utf-8 _*_

def beginview(dict):
    tempstr = '<div id="left"><p class="funcselect">功能选择</p>'
    templist = dict["functionlist"]
    dict.__delitem__("functionlist")
    templiststr = ""
    for k,v in dict.items():
        templiststr += '%s=%s&'%(k, v)
    for item in templist:
        tempstr = tempstr + '<li class="funclist">' \
                          + '<a href="/running.html?%sfunctiontype=%s&function=%s">%s</a>'%(templiststr, dict["functionName"],item["cmd_name"], item["cmd_commit"])\
                          +'</li>'
    tempstr = tempstr + "</div>"
    return tempstr
