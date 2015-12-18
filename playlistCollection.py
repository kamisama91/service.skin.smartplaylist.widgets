import helper
import moviePlaylist as mpl
import episodePlaylist as epl

MAX_PLAYLIST = 12

class PlaylistCollection():
    def __init__(self):
        self.Playlists = []
       
    def _getPlaylistInfos (self, playlistPath):
        _playlistName = ''
        _playlistType = ''
        if playlistPath != '':
            _doc = helper.loadXml(playlistPath)
            _playlistType = _doc.getElementsByTagName('smartplaylist')[0].attributes.item(0).value
            _playlistName = _doc.getElementsByTagName('name')[0].firstChild.nodeValue
        return _playlistName, _playlistType

    def _register(self, alias, path, settings):
        playlist = None
        playlistName, playlistType = self._getPlaylistInfos(path)

        if playlistType in ['episodes', 'tvshows']:
            playlist = epl.EpisodePlaylist(alias, path, playlistName, playlistType)
        elif playlistType == 'movies':
            playlist = mpl.MoviePlaylist(alias, path, playlistName)
        if playlist:
            self.Playlists.append(playlist)
            playlist.UpdateSettings(alias, settings)

    def Update(self, settings):
        configPlaylists = []
        count = 1
        while count <= MAX_PLAYLIST:
            alias = 'HomePlaylist%s' %count
            property = 'SkinWidgetPlaylists.%s' %alias
            if helper.getProperty(property) != '':
                configPlaylists.append({'alias': alias, 'path': helper.getProperty(property)})
            count += 1
        newPlaylistPath = [playlist['path'] for playlist in configPlaylists]
        for playlist in [playlist for playlist in self.Playlists if playlist.Path not in newPlaylistPath]:       
            playlist.Clean()
            self.Playlists.remove(playlist)
        for existingPlaylists in [existingPlaylist for existingPlaylist in self.Playlists if existingPlaylist.Path in [playlist['path'] for playlist in configPlaylists]]:
            existingPlaylist.Clean()
        for playlist in configPlaylists:
            existingPlaylists = [existingPlaylist for existingPlaylist in self.Playlists if existingPlaylist.Path == playlist['path']]
            if len(existingPlaylists) > 0:
                for existingPlaylist in existingPlaylists:
                    existingPlaylist.UpdateSettings(playlist['alias'], settings)
            else:
                self._register(playlist['alias'], playlist['path'], settings)

    def UpdateAllPlaylists(self, modes):
        for playlist in [playlist for playlist in self.Playlists]:
            playlist.Update(modes)
                
    def AddItem(self, type, id):
        for playlist in [playlist for playlist in self.Playlists if playlist.Type == type]:
            playlist.AddItem(id)
        
    def RemoveItem(self, type, id):
        for playlist in [playlist for playlist in self.Playlists if playlist.Type == type]:
            playlist.RemoveItem(id)
                
    def SetWatched(self, type, id):
        for playlist in [playlist for playlist in self.Playlists if playlist.Type == type]:
            playlist.SetWatched(id)
            
    def SetUnwatched(self, type, id):
        for playlist in [playlist for playlist in self.Playlists if playlist.Type == type]:
            playlist.SetUnWatched(id)      
    
    def StartPlaying(self, type, id):
        for playlist in [playlist for playlist in self.Playlists if playlist.Type == type]:
            playlist.StartPlaying(id)
    
    def StopPlaying(self, type, id, isEnded):
        for playlist in [playlist for playlist in self.Playlists if playlist.Type == type]:
            playlist.StopPlaying(id, isEnded)
         
    def GetPlaycountFromDatabase(self, type, id):
        playlists = [playlist for playlist in self.Playlists if playlist.Type == type]
        if len(playlists) > 0:
            return max([playlist.GetPlaycountFromDatabase(id) for playlist in playlists])        
        return 0
