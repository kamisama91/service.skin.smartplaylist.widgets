import sys
import xbmc
import xbmcgui
import xbmcaddon
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

from playlistCollection import PlaylistCollection
    

'''def logNotification(method, data):
    message = 'Notify: %s -> %s' % (method, data)
    file = open(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8') + "/notification.log", "a")
    file.write(message + '\r\n')
    file.close()'''
    
def getProperty ( _property ):
    return xbmcgui.Window( 10000 ).getProperty ( _property )
    
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
            addon = xbmcaddon.Addon()
            if int(addon.getSetting("random_method")) == 0 :
                # convert time to seconds, times 2 for 0,5 second sleep compensation
                targetTimet = int(float(addon.getSetting("random_timer"))) * 60 * 2
                timer += 1
                if timer == targetTimet:
                    self.Playlists.UpdateAllPlaylists(['Random'])
                    timer = 0    # reset counter
            if int(addon.getSetting("random_method")) == 2 :
                if  home_update and xbmcgui.getCurrentWindowId() == 10000:
                    self.Playlists.UpdateAllPlaylists(['Random'])
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
            elif playcount == 0:
                self.Playlists.SetUnwatched(contentType, contentId)
            elif playcount > 0 or self.Playlists.GetPlaycountFromDatabase(contentType, contentId) > 0:
                self.Playlists.SetWatched(contentType, contentId)
        elif method == 'VideoLibrary.OnRemove':
            contentId = data['id']
            contentType = data['type']
            self.Playlists.RemoveItem(contentType, contentId)
        elif method == 'Player.OnPlay':
            contentId = data['item']['id']
            contentType = data['item']['type']
            self.Playlists.StartPlaying(contentType, contentId)
        elif method == 'Player.OnStop':
            contentId = data['item']['id']
            contentType = data['item']['type']
            isEnded = data.get('end', False)
            self.Playlists.StopPlaying(contentType, contentId, isEnded)
            
    def _onSettingsChanged(self):
        addon = xbmcaddon.Addon()
        configPlaylists = []
        if addon.getSetting("autoselect_playlist") == 'true':
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
            if addon.getSetting("HomePlaylist1") != '':
                configPlaylists.append({'alias':'HomePlaylist1', 'path':addon.getSetting("HomePlaylist1")})
            if addon.getSetting("HomePlaylist2") != '':
                configPlaylists.append({'alias':'HomePlaylist2', 'path':addon.getSetting("HomePlaylist2")})
            if addon.getSetting("HomePlaylist3") != '':
                configPlaylists.append({'alias':'HomePlaylist3', 'path':addon.getSetting("HomePlaylist3")})
            if addon.getSetting("HomePlaylist4") != '':
                configPlaylists.append({'alias':'HomePlaylist4', 'path':addon.getSetting("HomePlaylist4")})
            if addon.getSetting("HomePlaylist5") != '':
                configPlaylists.append({'alias':'HomePlaylist5', 'path':addon.getSetting("HomePlaylist5")})  
            if addon.getSetting("HomePlaylist6") != '':
                configPlaylists.append({'alias':'HomePlaylist6', 'path':addon.getSetting("HomePlaylist6")})
            if addon.getSetting("HomePlaylist7") != '':
                configPlaylists.append({'alias':'HomePlaylist7', 'path':addon.getSetting("HomePlaylist7")})
            if addon.getSetting("HomePlaylist8") != '':
                configPlaylists.append({'alias':'HomePlaylist8', 'path':addon.getSetting("HomePlaylist8")})
            if addon.getSetting("HomePlaylist9") != '':
                configPlaylists.append({'alias':'HomePlaylist9', 'path':addon.getSetting("HomePlaylist9")})
            if addon.getSetting("HomePlaylist10") != '':
                configPlaylists.append({'alias':'HomePlaylist10', 'path':addon.getSetting("HomePlaylist10")})
            if addon.getSetting("HomePlaylist11") != '':
                configPlaylists.append({'alias':'HomePlaylist11', 'path':addon.getSetting("HomePlaylist11")})
            if addon.getSetting("HomePlaylist12") != '':
                configPlaylists.append({'alias':'HomePlaylist12', 'path':addon.getSetting("HomePlaylist12")})
        self.Playlists.Update(configPlaylists)



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
