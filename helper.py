import os
import sys
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import json
import xml.dom.minidom as xml
import sql

WINDOW = xbmcgui.Window(10000)

def log(txt):
    file = open(xbmcvfs.translatePath(get_addon_path()) + "/notification.log", "a", encoding='utf-8')
    file.write('%s\r' %txt)
    file.close()
    
def notify(message, duration = 2):
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
    
def load_json(jsonContent):
    return json.loads(jsonContent)
    
def load_xml(path):
    realpath = get_real_path(path)
    if os.path.exists(realpath):
        return xml.parse(realpath)
    else:
        return None
    
def read_addon_file(relativePath):
    file = open(xbmcvfs.translatePath(get_addon_path()) + "/" + relativePath, "r", encoding='utf-8')
    content = file.read()
    file.close()
    return content
    
def get_real_path(path):
    return xbmcvfs.translatePath(path)
    
def get_xbmc_major_version():
    json = execute_json_rpc('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
    return json['result']['version']['major']
    
def execute_json_rpc(request):
    jsonRpcResult = xbmc.executeJSONRPC(request)
    return load_json(jsonRpcResult)
    
def execute_sql_prepared_select(requestName, tokens):
    request = read_addon_file("/resources/sql/%s/%s.sql" % (sql.SqlConnexion.get_instance().videoDbType, requestName))
    for key, value in tokens.items():
        request = request.replace(key, value)
    return sql.SqlConnexion.get_instance().execute_sql_select(request)
    