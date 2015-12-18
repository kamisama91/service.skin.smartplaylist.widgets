import helper
import moviePlaylist as mpl
import episodePlaylist as epl

class PlaylistCollection():
    def __init__(self):
        self.Playlists = []
       
    def _getPlaylistInfos (self, playlistPath):
        _playlistName = ''
        _playlistType = ''
        if playlistPath != '':
            _doc = helper.loadXml(playlistPath)
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

    def _register(self, alias, path, settings):
        playlist = None
        playlistName, playlistType = self._getPlaylistInfos(path)

        if playlistType in ['Episode', 'TvShow']:
            playlist = epl.EpisodePlaylist(alias, path, playlistName)
        elif playlistType == 'Movie':
            playlist = mpl.MoviePlaylist(alias, path, playlistName)
        if playlist:
            self.Playlists.append(playlist)
            playlist.UpdateSettings(alias, settings)

    def Update(self, settings):
        configPlaylists = []
        if settings.getSetting("autoselect_playlist") == 'true':
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist1") != '':
                configPlaylists.append({'alias':'HomePlaylist1', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist1")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist2") != '':
                configPlaylists.append({'alias':'HomePlaylist2', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist2")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist3") != '':
                configPlaylists.append({'alias':'HomePlaylist3', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist3")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist4") != '':
                configPlaylists.append({'alias':'HomePlaylist4', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist4")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist5") != '':
                configPlaylists.append({'alias':'HomePlaylist5', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist5")})  
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist6") != '':
                configPlaylists.append({'alias':'HomePlaylist6', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist6")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist7") != '':
                configPlaylists.append({'alias':'HomePlaylist7', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist7")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist8") != '':
                configPlaylists.append({'alias':'HomePlaylist8', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist8")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist9") != '':
                configPlaylists.append({'alias':'HomePlaylist9', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist9")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist10") != '':
                configPlaylists.append({'alias':'HomePlaylist10', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist10")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist11") != '':
                configPlaylists.append({'alias':'HomePlaylist11', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist11")})
            if helper.getProperty("SkinWidgetPlaylists.HomePlaylist12") != '':
                configPlaylists.append({'alias':'HomePlaylist12', 'path':helper.getProperty("SkinWidgetPlaylists.HomePlaylist12")})
        else:
            if settings.getSetting("HomePlaylist1") != '':
                configPlaylists.append({'alias':'HomePlaylist1', 'path':settings.getSetting("HomePlaylist1")})
            if settings.getSetting("HomePlaylist2") != '':
                configPlaylists.append({'alias':'HomePlaylist2', 'path':settings.getSetting("HomePlaylist2")})
            if settings.getSetting("HomePlaylist3") != '':
                configPlaylists.append({'alias':'HomePlaylist3', 'path':settings.getSetting("HomePlaylist3")})
            if settings.getSetting("HomePlaylist4") != '':
                configPlaylists.append({'alias':'HomePlaylist4', 'path':settings.getSetting("HomePlaylist4")})
            if settings.getSetting("HomePlaylist5") != '':
                configPlaylists.append({'alias':'HomePlaylist5', 'path':settings.getSetting("HomePlaylist5")})  
            if settings.getSetting("HomePlaylist6") != '':
                configPlaylists.append({'alias':'HomePlaylist6', 'path':settings.getSetting("HomePlaylist6")})
            if settings.getSetting("HomePlaylist7") != '':
                configPlaylists.append({'alias':'HomePlaylist7', 'path':settings.getSetting("HomePlaylist7")})
            if settings.getSetting("HomePlaylist8") != '':
                configPlaylists.append({'alias':'HomePlaylist8', 'path':settings.getSetting("HomePlaylist8")})
            if settings.getSetting("HomePlaylist9") != '':
                configPlaylists.append({'alias':'HomePlaylist9', 'path':settings.getSetting("HomePlaylist9")})
            if settings.getSetting("HomePlaylist10") != '':
                configPlaylists.append({'alias':'HomePlaylist10', 'path':settings.getSetting("HomePlaylist10")})
            if settings.getSetting("HomePlaylist11") != '':
                configPlaylists.append({'alias':'HomePlaylist11', 'path':settings.getSetting("HomePlaylist11")})
            if settings.getSetting("HomePlaylist12") != '':
                configPlaylists.append({'alias':'HomePlaylist12', 'path':settings.getSetting("HomePlaylist12")})
        newPlaylistPath = [playlist['path'] for playlist in configPlaylists]
        for playlist in [playlist for playlist in self.Playlists if playlist.Path not in newPlaylistPath]:       
            playlist.Clean()
            self.Playlists.remove(playlist)
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
