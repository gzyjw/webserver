# _*_ coding: utf-8 _*_
paranamelist = tuple(["functionPort",\
                     "databaselist",\
                     "functionName",\
                     "functionServer",\
                     "proctollist",\
                     "functionPassword",\
                     "functionUser",\
                     "machineid",\
                     "MachineEquId",\
                     "viewstage"])

def makecommandlist(dict):
    tempstr = '<div id="left"><p class="funcselect">功能选择</p>'
    templist = dict["functionlist"]
    templiststr = ""
    for key in paranamelist:
        templiststr += '%s=%s&'%(key, dict[key])
    for item in templist:
        if item["cmd_name"] == "CMD_UPDATE_FONT":
            tempstr = tempstr + '<li class="funclist" id="%s">'%item["cmd_name"] \
                          + '<a href="/running.html?%sfontfilelist=1&functiontype=%s&function=%s">%s</a>'%(templiststr, dict["functionName"],item["cmd_name"], item["cmd_commit"])\
                          +'</li>'
        elif item["cmd_name"] == "CMD_UPDATE_PROG":
            tempstr = tempstr + '<li class="funclist" id="%s">'%item["cmd_name"] \
                          + '<a href="/running.html?%sprogfilelist=2&functiontype=%s&function=%s">%s</a>'%(templiststr, dict["functionName"],item["cmd_name"], item["cmd_commit"])\
                          +'</li>'
        else:
            tempstr = tempstr + '<li class="funclist" id="%s">'%item["cmd_name"] \
                          + '<a href="/running.html?%sfunctiontype=%s&function=%s">%s</a>'%(templiststr, dict["functionName"],item["cmd_name"], item["cmd_commit"])\
                          +'</li>'
    tempstr = tempstr + "</div>"
    return tempstr

def beginview(dict):
    tempstr = makecommandlist(dict)
    scriptstr = ""
    tempstr = list([tempstr, "", scriptstr, ""])
    return tempstr

def runningview(dict):
    tempstr = makecommandlist(dict)
    scriptstr = ""
    tempstr = list([tempstr, "", scriptstr, ""])
    return tempstr
