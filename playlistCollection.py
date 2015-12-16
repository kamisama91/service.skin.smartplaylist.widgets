import sys
import xbmc
from xml.dom.minidom import parse
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
from playlist import Playlist
from moviePlaylist import MoviePlaylist
from episodePlaylist import EpisodePlaylist


class PlaylistCollection():
    def __init__(self):
        self.Playlists = []
       
    def _getPlaylistInfos (self, playlistPath):
        _playlistName = ''
        _playlistType = ''
        if playlistPath != '':
            try:
                _doc = parse(xbmc.translatePath(playlistPath))
                _type = _doc.getElementsByTagName('smartplaylist')[0].attributes.item(0).value
                if _type == 'movies':
                   _playlistType = 'Movie'
                elif _type == 'episodes':
                   _playlistType = 'Episode'
                elif _type == 'tvshows':
                   _playlistType = 'TvShow'
                if _doc.getElementsByTagName('name'):
                    _playlistName = _doc.getElementsByTagName('name')[0].firstChild.nodeValue
                return _playlistName, _playlistType
            except:
                return _playlistName, _playlistType
        else:
            return _playlistName, _playlistType
       
    def _register(self, alias, path):
        playlist = None
        playlistName, playlistType = self._getPlaylistInfos(path)
        if playlistType in ['Episode', 'TvShow']:
            playlist = EpisodePlaylist(alias, path, playlistName)
        elif playlistType == 'Movie':
            playlist = MoviePlaylist(alias, path, playlistName)
        if playlist:
            self.Playlists.append(playlist)

            
    def Update(self, playlists):
        newPlaylistPath = [playlist['path'] for playlist in playlists]
        for playlist in [playlist for playlist in self.Playlists if playlist.Path not in newPlaylistPath]:       
            playlist.Clean()
            self.Playlists.remove(playlist)
        for playlist in playlists:
            existingPlaylists = [existingPlaylist for existingPlaylist in self.Playlists if existingPlaylist.Path == playlist['path']]
            if len(existingPlaylists) > 0:
                for existingPlaylist in existingPlaylists:
                    existingPlaylist.SetAlias(playlist['alias'])
            else:
                self._register(playlist['alias'], playlist['path'])

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

        

         