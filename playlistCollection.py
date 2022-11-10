import xbmc
import helper
from settings import Settings
import moviePlaylist as mpl
import episodePlaylist as epl

MAX_PLAYLIST = 15

class PlaylistCollection():
    def __init__(self):
        self.__playlists = []
       
    def __get_playlist_details (self, playlistPath):
        playlistName = ''
        playlistType = ''
        if playlistPath != '':
            playlistXml = helper.load_xml(playlistPath)
            playlistType = playlistXml.getElementsByTagName('smartplaylist')[0].attributes['type'].value
            playlistName = playlistXml.getElementsByTagName('name')[0].firstChild.nodeValue
        return playlistName, playlistType
    
    def __register(self, alias, path):
        playlist = None
        playlistName, playlistType = self.__get_playlist_details(path)
        if playlistType in ['episodes', 'tvshows']:
            playlist = epl.EpisodePlaylist(alias, path, playlistName, playlistType)
        elif playlistType == 'movies':
            playlist = mpl.MoviePlaylist(alias, path, playlistName, playlistType)
        if playlist:
            self.__playlists.append(playlist)
    
    def on_settings_updated(self):
        for playlist in self.__playlists:
            playlist.clean_items()
            self.__playlists.remove(playlist)
        for count in range(1, MAX_PLAYLIST+1):
            alias = 'service.skin.smartplaylist.widgets.SmartPlaylist%s' %count
            path = helper.get_property(alias)
            if path != '':
                self.__register(alias, path)
        self.__update_all_playlists(['Suggested', 'Recent', 'Random'])
    
    def on_timer_tick(self):
        if Settings.get_instance().randomUpdateOnTimer:
            self.__update_all_playlists(['Random'])
    
    def on_homescreen(self):
        if Settings.get_instance().randomUpdateOnHomeScreen:
            self.__update_all_playlists(['Random'])
    
    def on_library_updated(self, type, isDelete = False):
        self.__update_typed_playlists(type, ['Suggested', 'Recent', 'Random'] if (Settings.get_instance().randomUpdateOnLibraryUpdated or isDelete) else ['Suggested', 'Recent'])
    
    def on_item_played(self, id, type):
        database = "video" if type in ["movie", "episode", "musicvideo"] else "music"
        #Save status of started item
        self.__lastItemStatus = helper.execute_sql_prepared_select(database, "%s_status" %type, { "#ID#": str(id) })[0]
    
    def on_item_stopped(self, id, type):
        database = "video" if type in ["movie", "episode", "musicvideo"] else "music"
        #Wait status to be updated for stopped item
        itemUpdatedInDatabase = False
        while not itemUpdatedInDatabase:
            status = helper.execute_sql_prepared_select(database, "%s_status" %type, { "#ID#": str(id) })[0]
            itemUpdatedInDatabase = (status['lastplayed'] != self.__lastItemStatus['lastplayed'])
            xbmc.sleep(100)
        self.__update_typed_playlists(type, ['Suggested', 'Recent', 'Random'] if Settings.get_instance().randomUpdateOnLibraryUpdated else ['Suggested', 'Recent'])
    
    def __update_all_playlists(self, modes):
        for mode in [mode for mode in modes if mode in Settings.get_instance().get_enabled_modes()]:
            for playlist in [playlist for playlist in self.__playlists]:
                playlist.update_items(mode)
    
    def __update_typed_playlists(self, type, modes):
        for mode in [mode for mode in modes if mode in Settings.get_instance().get_enabled_modes()]:
            for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
                playlist.update_items(mode)

