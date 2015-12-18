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
    
def log(txt):
    file = open(xbmc.translatePath(getAddon().getAddonInfo('path')).decode('utf-8') + "/notification.log", "a")
    file.write(txt + '\r\n')
    file.close()
    
def getProperty ( _property ):
    return xbmcgui.Window( 10000 ).getProperty ( _property )
    
def setProperty ( _property, _value):
    xbmcgui.Window( 10000 ).setProperty ( _property, _value )

def clearProperty ( _property ):
    xbmcgui.Window( 10000 ).clearProperty ( _property )
    
def isHomeScreen ():
    return xbmcgui.getCurrentWindowId() == 10000
    
def getAddon():
    return xbmcaddon.Addon()
    
def currentTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    
def loadJson(json):
    return simplejson.loads(json)

def loadXml(path):
    return parse(realPath(path))
    
def splitPath(path):
    return os.path.split(path)
    
def realPath(path):
    return xbmc.translatePath(path)
    
def deleteFile(path):
    os.remove(realPath(path))
    
def executeJsonRpc(json):
    return loadJson(unicode(xbmc.executeJSONRPC(json), 'utf-8', errors='ignore'))
