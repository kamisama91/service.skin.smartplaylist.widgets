import os
import sys
import time
import uuid
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
from xml.dom.minidom import parse
import json as simplejson

WINDOW = xbmcgui.Window(10000)
# This is a throwaway variable to deal with a python bug
throwaway = time.strptime('20110101','%Y%m%d')

def log(txt):
    file = open(xbmcvfs.translatePath(get_addon_path()) + "/notification.log", "a")
    file.write('%s\r' %txt)
    file.close()
    
def notify(message, duration):
    xbmc.executebuiltin('Notification(%s,%s,%d,%s)' %(get_addon_name(), message, 1000*duration, xbmcvfs.translatePath(get_addon_path())+"/icon.png"))
    
def get_property(property):
    return WINDOW.getProperty(property)
    
def set_property(property, value):
    WINDOW.setProperty(property, value)
    
def clear_property(property):
    WINDOW.clearProperty(property)
    
def is_home_screen():
    return xbmcgui.getCurrentWindowId() == 10000
    
def get_addon_config():
    return xbmcaddon.Addon()
    
def get_addon_path():
    return xbmcaddon.Addon().getAddonInfo('path')
    
def get_addon_name():
    return xbmcaddon.Addon().getAddonInfo('name')
    
def current_timestamp():
    return time.time()
    
def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_timestamp()))
    
def date(datetimeString):
    datetimeObject = time.strptime(datetimeString, "%Y-%m-%d %H:%M:%S")
    return time.strftime("%Y-%m-%d 00:00:00", datetimeObject)
    
def load_json(json):
    return simplejson.loads(json)

def load_xml(path):
    return parse(get_real_path(path))
    
def save_xml(path, xmlDocument):
    file_handle = open(get_real_path(path), "w")
    xmlDocument.writexml(file_handle)
    file_handle.close()
    
def delete_xml(path):
    if path != '':
        realPath = get_real_path(path)
        if os.path.exists(realPath):
            os.remove(realPath)
    
def split_path(path):
    splitPath = os.path.split(path)
    tokens = []
    tokens.append(splitPath[0])
    tokens.append(splitPath[1])    
    tokens[0] = tokens[0] + ('/' if '/' in tokens[0] else '\\')
    tokens[0] = tokens[0].replace('\\', '\\\\')
    return tokens
    
def split_filename(filename):
    return os.path.splitext(filename)
    
def get_real_path(path):
    return xbmcvfs.translatePath(path)
    
def execute_json_rpc(request):
    t1 = current_timestamp()
    jsonRpcResult = xbmc.executeJSONRPC(request)
    response = load_json(jsonRpcResult)
    t2 = current_timestamp()
    #log("request: %s\rresponse: %s\rduration: %d seconds\r" %(request, response, (t2-t1)))
    return response
    
def get_uuid():
    return uuid.uuid4().hex
