import xbmc
import helper
from settings import Settings
from sql import SqlConnexion
import playlistCollection as plc

class Main:
    def __init__(self):
        self.__collection = plc.PlaylistCollection()
        self.__monitor = WidgetsMonitor(onNotificationCallback = self.__on_notification_cb, onSettingsChangedCallback = self.__on_settings_changed_cb)
        self.__on_settings_changed_cb()
        self.__daemon()

    def __daemon(self):
        timer = 0
        home_update = False
        while (not self.__monitor.abortRequested()):
            xbmc.sleep(500)
            if Settings.get_instance().is_reload_addon_config_required():
                self.__on_settings_changed_cb()
            if Settings.get_instance().randomTimer > 0 and ++timer == (Settings.get_instance().randomTimer * 60 * 2):
                timer = 0
                self.__collection.on_timer_tick()
            if home_update and helper.is_home_screen():
                home_update = False
                self.__collection.on_homescreen()
            elif not home_update and not helper.is_home_screen():
                home_update = True
    
    def __on_notification_cb(self, method, data):
        if method == 'VideoLibrary.OnUpdate':
            contentId = data.get('item', data)['id']
            contentType = data.get('item', data)['type']
            self.__collection.on_library_updated(contentType)
        elif method == 'VideoLibrary.OnRemove':
            contentId = data.get('item', data)['id']
            contentType = data.get('item', data)['type']
            self.__collection.on_library_updated(contentType, True)
        elif method == 'Player.OnPlay':
            contentId = data.get('item', data)['id']
            contentType = data.get('item', data)['type']
            self.__collection.on_item_played(contentId, contentType)
        elif method == 'Player.OnStop':
            contentId = data.get('item', data)['id']
            contentType = data.get('item', data)['type']
            self.__collection.on_item_stopped(contentId, contentType)
    
    def __on_settings_changed_cb(self):
        Settings.get_instance().reload_addon_config()
        self.__collection.on_settings_updated()

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
    SqlConnexion.get_instance()
    Main()
    del WidgetsMonitor
    del Main
    SqlConnexion.drop_instance()
