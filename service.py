import xbmc
import helper
import playlistCollection as plc

class Main:
    def __init__(self):
        self.__settings = None
        self.__collection = plc.PlaylistCollection()
        self.__monitor = WidgetsMonitor(onNotificationCallback = self.__on_notification_cb, onSettingsChangedCallback = self.__on_settings_changed_cb)
        helper.set_property('SkinWidgetPlaylists.ReloadSettings', 'false')
        self.__on_settings_changed_cb()        
        self.__daemon()

    def __daemon(self):
        home_update = False
        timer = 0
        while (not xbmc.abortRequested):
            xbmc.sleep(500)
            if helper.get_property('SkinWidgetPlaylists.ReloadSettings') == 'true':
                helper.set_property('SkinWidgetPlaylists.ReloadSettings', 'false')
                self.__on_settings_changed_cb()
            if int(self.__settings.getSetting("random_method")) == 0 :
                # convert time to seconds, times 2 for 0,5 second sleep compensation
                targetTimet = int(float(self.__settings.getSetting("random_timer"))) * 60 * 2
                timer += 1
                if timer == targetTimet:
                    self.__collection.update_all_playlists(['Random'])
                    timer = 0
            if int(self.__settings.getSetting("random_method")) == 2 :
                if  home_update and helper.is_home_screen():
                    self.__collection.update_all_playlists(['Random'])
                    home_update = False
                elif not home_update and not helper.is_home_screen():
                    home_update = True
    
    def __on_notification_cb(self, method, data):
        if method == 'VideoLibrary.OnUpdate':
            contentId = data['item']['id']
            contentType = data['item']['type']
            playcount = data.get('playcount', -1)
            if not self.__collection.contains_item(contentType, contentId):
                self.__collection.add_item(contentType, contentId)
            elif playcount == 0:
                self.__collection.set_unwatched(contentType, contentId)
            elif playcount > 0 or self.__collection.get_playcount_from_database(contentType, contentId) > 0:
                self.__collection.set_watched(contentType, contentId)
        elif method == 'VideoLibrary.OnRemove':
            contentId = data['id']
            contentType = data['type']
            self.__collection.remove_item(contentType, contentId)
        elif method == 'Player.OnPlay':
            contentId = data['item']['id']
            contentType = data['item']['type']
            self.__collection.start_playing(contentType, contentId)
        elif method == 'Player.OnStop':
            contentId = data['item']['id']
            contentType = data['item']['type']
            isEnded = data.get('end', False)
            self.__collection.stop_playing(contentType, contentId, isEnded)
            
    def __on_settings_changed_cb(self):
        self.__settings = helper.get_addon_config()
        self.__collection.update(self.__settings)
        
class WidgetsMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        self.__onNotificationCallback = kwargs['onNotificationCallback']
        self.__onSettingsChangedCallback = kwargs['onSettingsChangedCallback']
        xbmc.Monitor.__init__(self)
        
    def onNotification(self, sender, method, data):
        self.__onNotificationCallback(method, helper.load_json(data))

    def onSettingsChanged(self):
        self.__onSettingsChangedCallback()
         
if (__name__ == "__main__"):
    Main()
    del WidgetsMonitor
    del Main
