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
    
class Main:
    def __init__(self):
        self.Playlists = PlaylistCollection()
        self.Playlists.Register('HomePlaylist1', 'special://profile/playlists/video/Films.xsp')
        self.Playlists.Register('HomePlaylist2', 'special://profile/playlists/video/FilmsAnimes.xsp')
        self.Playlists.Register('HomePlaylist3', 'special://profile/playlists/video/Series.xsp')
        self.Playlists.Register('HomePlaylist4', 'special://profile/playlists/video/SeriesAnimees.xsp')        
        self.Monitor = Widgets_Monitor(onNotificationCallback = self._onNotification, onSettingsChangedCallback = self._onSettingsChanged)
        self._daemon()

    def _daemon(self):
        while (not xbmc.abortRequested):
            xbmc.sleep(500)
    
    def _onNotification(self, method, data):
        if method == 'VideoLibrary.OnUpdate':
            contentId = data['item']['id']
            contentType = data['item']['type']
            playcount = data.get('playcount', -1)
            transaction = data.get('transaction', False)
            if transaction == True:
                self.Playlists.AddItem(contentType, contentId)
            elif playcount == 0:
                self.Playlists.SetUnwatched(contentType, contentId)
            elif playcount > 0:
                self.Playlists.SetWatched(contentType, contentId)
        elif method == 'VideoLibrary.OnRemove':
            contentId = data['id']
            contentType = data['type']
            self.Playlists.RemoveItem(contentType, contentId)
    
    def _onSettingsChanged(self):
        #logNotification('Settings updated')
        return
        
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
