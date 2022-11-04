import threading
import helper
import moviePlaylist as mpl
import episodePlaylist as epl
import musicvideoPlaylist as mvpl
import songPlaylist as spl

MAX_PLAYLIST = 15

class PlaylistCollection():
    def __init__(self):
        self.__playlists = []
       
    def __get_playlist_details (self, playlistPath):
        playlistName = ''
        playlistType = ''
        if playlistPath != '':
            playlistXml = helper.load_xml(playlistPath)
            playlistType = playlistXml.getElementsByTagName('smartplaylist')[0].attributes.item(0).value
            playlistName = playlistXml.getElementsByTagName('name')[0].firstChild.nodeValue
        return playlistName, playlistType

    def __register(self, alias, path, settings):
        playlist = None
        playlistName, playlistType = self.__get_playlist_details(path)
        if playlistType in ['episodes', 'tvshows']:
            playlist = epl.EpisodePlaylist(alias, path, playlistName, playlistType)
        elif playlistType == 'movies':
            playlist = mpl.MoviePlaylist(alias, path, playlistName, playlistType)
        elif playlistType == 'musicvideos':
            playlist = mvpl.MusicVideoPlaylist(alias, path, playlistName, playlistType)
        elif playlistType in ['songs', 'albums', 'artists']:
            playlist = spl.SongPlaylist(alias, path, playlistName, playlistType)
        if playlist:
            self.__playlists.append(playlist)
            playlist.reload_paylist_content()
            playlist.update_settings(alias, settings)
    
    def update(self, settings):
        t1 = helper.current_timestamp()
        threads = []
        configPlaylists = []
        count = 1
        while count <= MAX_PLAYLIST:
            property = 'service.skin.smartplaylist.widgets.SmartPlaylist%s' %count
            if helper.get_property(property) != '':
                configPlaylists.append({'alias': property, 'path': helper.get_property(property)})
            count += 1
        newPlaylistPath = [playlist['path'] for playlist in configPlaylists]
        for playlist in [playlist for playlist in self.__playlists if playlist.playlistPath not in newPlaylistPath]:
            playlist.clean()
            self.__playlists.remove(playlist)
        for playlist in [existingPlaylist for existingPlaylist in self.__playlists if existingPlaylist.playlistPath in [playlist['path'] for playlist in configPlaylists]]:
            playlist.clean()
        for playlist in configPlaylists:
            existingPlaylists = [existingPlaylist for existingPlaylist in self.__playlists if existingPlaylist.playlistPath == playlist['path']]
            if len(existingPlaylists) > 0:
                for existingPlaylist in existingPlaylists:
                    existingPlaylist.update_settings(playlist['alias'], settings)
            else:
                threads.append(threading.Thread(target=self.__register, args=(playlist['alias'], playlist['path'], settings, )))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        t2 = helper.current_timestamp()
        #helper.notify("%s: %d seconds" %("Loaded", t2-t1), 2)
    
    def update_all_playlists(self, modes):
        for playlist in [playlist for playlist in self.__playlists]:
            playlist.update(modes)
       
    def reload_paylist_content(self, type):
        for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
            playlist.reload_paylist_content()
    
    def contains_item(self, type, id):
        itemFound = False
        for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
            itemFound = itemFound or playlist.contains_item(id)
        return itemFound
            
    def add_item(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
            playlist.add_item(id)
        
    def remove_item(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
            playlist.remove_item(id)
                
    def set_watched(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
            playlist.set_watched(id)
            
    def set_unwatched(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
            playlist.set_unwatched(id)
    
    def start_playing(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
            playlist.start_playing(id)
    
    def stop_playing(self, type, id, isEnded):
        for playlist in [playlist for playlist in self.__playlists if playlist.itemType == type]:
            playlist.stop_playing(id, isEnded)
