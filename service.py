import xbmc
import helper
import playlistCollection as plc

class Main:
    def __init__(self):
        self.Settings = None
        self.Playlists = plc.PlaylistCollection()
        self.Monitor = Widgets_Monitor(onNotificationCallback = self._onNotification, onSettingsChangedCallback = self._onSettingsChanged)
        helper.setProperty('SkinWidgetPlaylists.ReloadSettings', 'false')
        self._onSettingsChanged()        
        self._daemon()

    def _daemon(self):
        home_update = False
        timer = 0
        while (not xbmc.abortRequested):
            xbmc.sleep(500)
            if helper.getProperty('SkinWidgetPlaylists.ReloadSettings') == 'true':
                helper.setProperty('SkinWidgetPlaylists.ReloadSettings', 'false')
                self._onSettingsChanged()
            if int(self.Settings.getSetting("random_method")) == 0 :
                # convert time to seconds, times 2 for 0,5 second sleep compensation
                targetTimet = int(float(self.Settings.getSetting("random_timer"))) * 60 * 2
                timer += 1
                if timer == targetTimet:
                    self.Playlists.UpdateAllPlaylists(['Random'])
                    timer = 0
            if int(self.Settings.getSetting("random_method")) == 2 :
                if  home_update and helper.isHomeScreen():
                    self.Playlists.UpdateAllPlaylists(['Random'])
                    home_update = False
                elif not home_update and not helper.isHomeScreen():
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
        self.Settings = helper.getAddon()
        self.Playlists.Update(self.Settings)
        
class Widgets_Monitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        self.onNotificationCallback = kwargs['onNotificationCallback']
        self.onSettingsChangedCallback = kwargs['onSettingsChangedCallback']
        xbmc.Monitor.__init__(self)
        
    def onNotification(self, sender, method, data):
        self.onNotificationCallback(method, helper.loadJson(data))

    def onSettingsChanged(self):
        self.onSettingsChangedCallback()
         
if (__name__ == "__main__"):
    Main()
    del Widgets_Monitor
    del Main
