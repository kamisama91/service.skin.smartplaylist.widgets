import xbmc
from xml.dom.minidom import parse

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
       
    def Register(self, alias, path):
        playlist = None
        playlistName, playlistType = self._getPlaylistInfos(path)
        if playlistType in ['Episode', 'TvShow']:
            playlist = EpisodePlaylist(alias, path, playlistName)
        elif playlistType == 'Movie':
            playlist = MoviePlaylist(alias, path, playlistName)
        if playlist:
            self.Playlists.append(playlist)
            playlist.SetPlaylistProperties()
            playlist.RefreshItems('Random')
            playlist.RefreshItems('Recent')
            playlist.RefreshItems('Suggested')

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