import helper
import moviePlaylist as mpl
import episodePlaylist as epl

MAX_PLAYLIST = 12

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
            playlist = mpl.MoviePlaylist(alias, path, playlistName)
        if playlist:
            self.__playlists.append(playlist)
            playlist.update_settings(alias, settings)

    def update(self, settings):
        configPlaylists = []
        count = 1
        while count <= MAX_PLAYLIST:
            alias = 'HomePlaylist%s' %count
            property = 'SkinWidgetPlaylists.%s' %alias
            if helper.get_property(property) != '':
                configPlaylists.append({'alias': alias, 'path': helper.get_property(property)})
            count += 1
        newPlaylistPath = [playlist['path'] for playlist in configPlaylists]
        for playlist in [playlist for playlist in self.__playlists if playlist.path not in newPlaylistPath]:       
            playlist.Clean()
            self.__playlists.remove(playlist)
        for existingPlaylists in [existingPlaylist for existingPlaylist in self.__playlists if existingPlaylist.path in [playlist['path'] for playlist in configPlaylists]]:
            existingPlaylist.Clean()
        for playlist in configPlaylists:
            existingPlaylists = [existingPlaylist for existingPlaylist in self.__playlists if existingPlaylist.path == playlist['path']]
            if len(existingPlaylists) > 0:
                for existingPlaylist in existingPlaylists:
                    existingPlaylist.update_settings(playlist['alias'], settings)
            else:
                self.__register(playlist['alias'], playlist['path'], settings)

    def update_all_playlists(self, modes):
        for playlist in [playlist for playlist in self.__playlists]:
            playlist.update(modes)
                
    def contains_item(self, type, id):
        itemFound = False
        for playlist in [playlist for playlist in self.__playlists if playlist.type == type]:
            itemFound = itemFound or playlist.contains_item(id)
        return itemFound
            
    def add_item(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.type == type]:
            playlist.add_item(id)
        
    def remove_item(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.type == type]:
            playlist.remove_item(id)
                
    def set_watched(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.type == type]:
            playlist.set_watched(id)
            
    def set_unwatched(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.type == type]:
            playlist.set_unwatched(id)      
    
    def start_playing(self, type, id):
        for playlist in [playlist for playlist in self.__playlists if playlist.type == type]:
            playlist.start_playing(id)
    
    def stop_playing(self, type, id, isEnded):
        for playlist in [playlist for playlist in self.__playlists if playlist.type == type]:
            playlist.stop_playing(id, isEnded)
         
    def get_playcount_from_database(self, type, id):
        playlists = [playlist for playlist in self.__playlists if playlist.type == type]
        if len(playlists) > 0:
            return max([playlist.get_playcount_from_database(id) for playlist in playlists])        
        return 0
