import os
import sys
import time
import uuid
import xbmc
import xbmcgui
import xbmcaddon
from xml.dom.minidom import parse
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

WINDOW = xbmcgui.Window(10000)
# This is a throwaway variable to deal with a python bug
throwaway = time.strptime('20110101','%Y%m%d')

def log(txt):
    file = open(xbmc.translatePath(get_addon_path()).decode('utf-8') + "/notification.log", "a")
    file.write('%s\r\n' %txt)
    file.close()
    
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
    
def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

def date(datetimeString):
    datetimeObject = time.strptime(datetimeString, "%Y-%m-%d %H:%M:%S")
    return time.strftime("%Y-%m-%d 00:00:00", datetimeObject)
    
def load_json(json):
    return simplejson.loads(json)

def load_xml(path):
    return parse(get_real_path(path))
    
def save_xml(path, xmlDocument):
    file_handle = open(get_real_path(path),"wb")
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
    return xbmc.translatePath(path)
        
def execute_json_rpc(json):
    jsonRpcResult = xbmc.executeJSONRPC(json.encode('utf-8', 'ignore'))
    return load_json(jsonRpcResult.decode('utf-8', 'ignore'))

def get_uuid():
    return uuid.uuid4().hex
