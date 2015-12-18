import os
import sys
import time
import xbmc
import xbmcgui
import xbmcaddon
from xml.dom.minidom import parse
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

WINDOW = xbmcgui.Window(10000)

def log(txt):
    file = open(xbmc.translatePath(get_addon_config().getAddonInfo('path')).decode('utf-8') + "/notification.log", "a")
    file.write(txt + '\r\n')
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
    
def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    
def load_json(json):
    return simplejson.loads(json)

def load_xml(path):
    return parse(get_real_path(path))
    
def split_path(path):
    return os.path.split(path)
    
def get_real_path(path):
    return xbmc.translatePath(path)
        
def execute_json_rpc(json):
    return load_json(unicode(xbmc.executeJSONRPC(json), 'utf-8', errors='ignore'))
