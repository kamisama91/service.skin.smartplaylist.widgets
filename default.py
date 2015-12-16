import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import random
import datetime
import _strptime
import urllib
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

from playlistCollection import PlaylistCollection
    
__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__localize__     = __addon__.getLocalizedString
__addonpath__    = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')

def log(txt):
    message = '%s: %s' % (__addonname__, txt.encode('ascii', 'ignore'))
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)
        
def setProperty ( _property, _value ):
    xbmcgui.Window( 10000 ).setProperty ( _property, _value )
        
def getProperty ( _property ):
    return xbmcgui.Window( 10000 ).getProperty ( _property )

'''def logNotification(method, data):
    message = 'Notify: %s -> %s' % (method, data)
    file = open(__addonpath__ + "/notification.log", "a")
    file.write(message + '\r\n')
    file.close()'''
    
class Main:
    def __init__(self):
        self.Playlists = PlaylistCollection()
        self.Monitor = Widgets_Monitor(onNotificationCallback = self._onNotification, onSettingsChangedCallback = self._onSettingsChanged)
        self._onSettingsChanged()       
        self._daemon()

    def _daemon(self):
        home_update = False
        timer = 0
        while (not xbmc.abortRequested):
            xbmc.sleep(500)
            if int(__addon__.getSetting("random_method")) == 0 :
                # convert time to seconds, times 2 for 0,5 second sleep compensation
                targetTimet = int(float(__addon__.getSetting("random_timer"))) * 60 * 2
                timer += 1
                if timer == targetTimet:
                    self.Playlists.RefreshAll('Random')
                    timer = 0    # reset counter
            if int(__addon__.getSetting("random_method")) == 2 :
                if  home_update and xbmcgui.getCurrentWindowId() == 10000:
                    self.Playlists.RefreshAll('Random')
                    home_update = False
                elif not home_update and xbmcgui.getCurrentWindowId() != 10000:
                    home_update = True
    
    def _onNotification(self, method, data):
        if method == 'VideoLibrary.OnUpdate':
            contentId = data['item']['id']
            contentType = data['item']['type']
            playcount = data.get('playcount', -1)
            transaction = data.get('transaction', False)
            if transaction == True:
                self.Playlists.AddItem(contentType, contentId)
                self.Playlists.RefreshByType(contentType, 'Suggested')
                self.Playlists.RefreshByType(contentType, 'Recent')
                if int(__addon__.getSetting("random_method")) == 1:
                    self.Playlists.RefreshByType(contentType, 'Random')
            elif playcount == 0:
                self.Playlists.SetUnwatched(contentType, contentId)
                self.Playlists.RefreshByType(contentType, 'Suggested')
                self.Playlists.RefreshByType(contentType, 'Recent')
                if int(__addon__.getSetting("random_method")) == 1:
                    self.Playlists.RefreshByType(contentType, 'Random')
            elif playcount > 0:
                self.Playlists.SetWatched(contentType, contentId)
                self.Playlists.RefreshByType(contentType, 'Suggested')
                self.Playlists.RefreshByType(contentType, 'Recent')
                if int(__addon__.getSetting("random_method")) == 1:
                    self.Playlists.RefreshByType(contentType, 'Random')
            elif self.Playlists.GetPlaycountFromDatabase(contentType, contentId) > 0:
                self.Playlists.SetWatched(contentType, contentId)
                self.Playlists.RefreshByType(contentType, 'Suggested')
                self.Playlists.RefreshByType(contentType, 'Recent')
                if int(__addon__.getSetting("random_method")) == 1:
                    self.Playlists.RefreshByType(contentType, 'Random')
        elif method == 'VideoLibrary.OnRemove':
            contentId = data['id']
            contentType = data['type']
            self.Playlists.RemoveItem(contentType, contentId)
            self.Playlists.RefreshByType(contentType, 'Suggested')
            self.Playlists.RefreshByType(contentType, 'Recent')
            if int(__addon__.getSetting("random_method")) == 1:
                self.Playlists.RefreshByType(contentType, 'Random')
        elif method == 'Player.OnPlay':
            contentId = data['item']['id']
            contentType = data['item']['type']
            self.Playlists.StartPlaying(contentType, contentId)
        elif method == 'Player.OnStop':
            contentType = data['item']['id']
            contentType = data['item']['type']
            isEnded = data.get('end', False)
            if isEnded == False:
                self.Playlists.RefreshByType(contentType, 'Suggested')  #Suggested may look at lastplayed
            
    def _onSettingsChanged(self):
        configPlaylists = []
        if __addon__.getSetting("autoselect_playlist") == 'true':
            if getProperty("SkinWidgetPlaylists.HomePlaylist1") != '':
                configPlaylists.append({'alias':'HomePlaylist1', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist1")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist2") != '':
                configPlaylists.append({'alias':'HomePlaylist2', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist2")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist3") != '':
                configPlaylists.append({'alias':'HomePlaylist3', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist3")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist4") != '':
                configPlaylists.append({'alias':'HomePlaylist4', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist4")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist5") != '':
                configPlaylists.append({'alias':'HomePlaylist5', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist5")})  
            if getProperty("SkinWidgetPlaylists.HomePlaylist6") != '':
                configPlaylists.append({'alias':'HomePlaylist6', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist6")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist7") != '':
                configPlaylists.append({'alias':'HomePlaylist7', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist7")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist8") != '':
                configPlaylists.append({'alias':'HomePlaylist8', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist8")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist9") != '':
                configPlaylists.append({'alias':'HomePlaylist9', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist9")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist10") != '':
                configPlaylists.append({'alias':'HomePlaylist10', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist10")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist11") != '':
                configPlaylists.append({'alias':'HomePlaylist11', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist11")})
            if getProperty("SkinWidgetPlaylists.HomePlaylist12") != '':
                configPlaylists.append({'alias':'HomePlaylist12', 'path':getProperty("SkinWidgetPlaylists.HomePlaylist12")})
        else:
            if __addon__.getSetting("HomePlaylist1") != '':
                configPlaylists.append({'alias':'HomePlaylist1', 'path':__addon__.getSetting("HomePlaylist1")})
            if __addon__.getSetting("HomePlaylist2") != '':
                configPlaylists.append({'alias':'HomePlaylist2', 'path':__addon__.getSetting("HomePlaylist2")})
            if __addon__.getSetting("HomePlaylist3") != '':
                configPlaylists.append({'alias':'HomePlaylist3', 'path':__addon__.getSetting("HomePlaylist3")})
            if __addon__.getSetting("HomePlaylist4") != '':
                configPlaylists.append({'alias':'HomePlaylist4', 'path':__addon__.getSetting("HomePlaylist4")})
            if __addon__.getSetting("HomePlaylist5") != '':
                configPlaylists.append({'alias':'HomePlaylist5', 'path':__addon__.getSetting("HomePlaylist5")})  
            if __addon__.getSetting("HomePlaylist6") != '':
                configPlaylists.append({'alias':'HomePlaylist6', 'path':__addon__.getSetting("HomePlaylist6")})
            if __addon__.getSetting("HomePlaylist7") != '':
                configPlaylists.append({'alias':'HomePlaylist7', 'path':__addon__.getSetting("HomePlaylist7")})
            if __addon__.getSetting("HomePlaylist8") != '':
                configPlaylists.append({'alias':'HomePlaylist8', 'path':__addon__.getSetting("HomePlaylist8")})
            if __addon__.getSetting("HomePlaylist9") != '':
                configPlaylists.append({'alias':'HomePlaylist9', 'path':__addon__.getSetting("HomePlaylist9")})
            if __addon__.getSetting("HomePlaylist10") != '':
                configPlaylists.append({'alias':'HomePlaylist10', 'path':__addon__.getSetting("HomePlaylist10")})
            if __addon__.getSetting("HomePlaylist11") != '':
                configPlaylists.append({'alias':'HomePlaylist11', 'path':__addon__.getSetting("HomePlaylist11")})
            if __addon__.getSetting("HomePlaylist12") != '':
                configPlaylists.append({'alias':'HomePlaylist12', 'path':__addon__.getSetting("HomePlaylist12")})
        for item in configPlaylists:
            self.Playlists.Register(item['alias'], item['path'])
            self.Playlists.RefreshByAlias(item['alias'], 'All')


class Widgets_Monitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        self.onNotificationCallback = kwargs['onNotificationCallback']
        self.onSettingsChangedCallback = kwargs['onSettingsChangedCallback']
        xbmc.Monitor.__init__(self)
        
    def onNotification(self, sender, method, data):
        self.onNotificationCallback(method, simplejson.loads(data))

    def onSettingsChanged(self):
        self.onSettingsChangedCallback()
         
if (__name__ == "__main__"):
    Main()
    del Widgets_Monitor
    del Main
