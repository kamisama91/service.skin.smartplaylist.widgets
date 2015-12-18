import urllib
import xbmc
import random
import helper
import playlist as pl

class EpisodePlaylist(pl.Playlist):
    def __init__(self, alias, path, name, type):
        pl.Playlist.__init__(self, alias, path, name, 'episode')
        self.RealType = type
        self.IgnoreSpecials = False

    def _readSettings(self, settings):
        pl.Playlist._readSettings(self, settings)
        if settings:
            self.IgnoreSpecials = settings.getSetting("ignore_specials") == 'true'
            
    def _setPlaylistProperties(self):
        pl.Playlist._setPlaylistProperties(self)
        helper.setProperty("%s.TvShows" %self.Alias, str(self._getTvShowCount()))
    
    def _setOnePlaylistItemsProperties(self, property, item):
        pl.Playlist._setOnePlaylistItemsProperties(self, property, item)
        if item:
            helper.setProperty("%s.EpisodeNo"    % property, "S%.2dE%.2d" %(float(item.get('season')), float(item.get('episode'))))
            helper.setProperty("%s.TVshowTitle"  % property, item.get('showtitle'))
            helper.setProperty("%s.Art(thumb)"   % property, item['art'].get('thumb',''))
            helper.setProperty("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))
   
    def _clearPlaylistProperties(self):
        pl.Playlist._clearPlaylistProperties(self)
        for property in ['Name', 'Type', 'Count', 'Watched', 'Unwatched']:
            helper.clearProperty('%s.%s' %(self.Alias, property))
        
    def ClearOnePlaylistItemsProperties(self, property):
        pl.Playlist.ClearOnePlaylistItemsProperties(self, property)
        for item in ['EpisodeNo', 'TVshowTitle', 'Art(thumb)', 'Art(fanart)']:
            helper.clearProperty('%s.%s' %(property, item)) 
                
    def _getTvShowCount(self):
        showIds = set([item['tvshowid'] for item in self.Items])
        return len(showIds)
        
    def _fetchFromPlaylist(self, directory):
        _result = []
        _json_set_response = helper.executeJsonRpc('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "video", "properties": ["title", "tvshowid", "showtitle", "season", "episode", "art", "dateadded", "playcount", "lastplayed", "resume"]}, "id": 1}' %(directory))
        _files = _json_set_response.get( "result", {} ).get( "files" )
        if _files:
            for _file in _files:
                if xbmc.abortRequested:
                    break
                if _file['filetype'] == 'directory':
                    directoryFiles = self._fetchFromPlaylist(_file['file'])
                    for directoryFile in directoryFiles:
                        id = directoryFile.get('id', -1)
                        if id != -1 and id not in [file['id'] for file in _result]:
                            _result.append(directoryFile)
                else:
                    id = _file.get('id', -1)
                    if id != -1 and id not in [file['id'] for file in _result]:
                        _result.append(_file)
        return _result

    def _getDetails(self, id):
        _json_set_response = helper.executeJsonRpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": ["file", "tvshowid", "showtitle", "season", "episode", "playcount"], "episodeid":%s }, "id": 1}' %id)
        details = _json_set_response.get( 'result', {} ).get( 'episodedetails', None )
        if details:
            details['id'] = details['episodeid']
        return details
        
    def _getRandomItems(self):
        items = [item for item in self.Items if item['season']>0] if self.IgnoreSpecials else [item for item in self.Items]
        items = [item for item in items if item['playcount']==0] if self.RandomOnlyUnplayed else [item for item in items]
        random.shuffle(items)
        return items[:self.ItemLimit]
        
    def _getRecentItems(self):
        items = [item for item in self.Items if item['season']>0] if self.IgnoreSpecials else [item for item in self.Items]
        items = [item for item in items if item['playcount']==0] if self.RecentOnlyUnplayed else [item for item in items]
        items = sorted(items, key=lambda x: x['dateadded'], reverse=True)
        return items[:self.ItemLimit]
        
    def _getSuggestedItems(self):
        playedTvShows = []
        playedTvShowIds = set([item['tvshowid'] for item in self.Items if item['playcount']>0])      
        for playedTvShowId in playedTvShowIds:
            lastPlayed = max([item['lastplayed'] for item in self.Items if item['tvshowid']==playedTvShowId])
            playedTvShows.append({'tvshowid':playedTvShowId, 'lastplayed':lastPlayed})
        nextEpisodes = []
        playedTvShows = sorted(playedTvShows, key=lambda x: x['lastplayed'], reverse=True)
        for playedTvShow in playedTvShows:
            episodes = [item for item in self.Items if item['playcount']==0 and item['season']>0 and item['tvshowid']==playedTvShow['tvshowid']]
            episodes = sorted(episodes, key=lambda x: [x['season'],x['episode']], reverse=False)
            if len(episodes) > 0:
                nextEpisodes.append(episodes[0])
            elif not self.IgnoreSpecials:
                episodes = [item for item in self.Items if item['playcount']==0 and item['season']==0 and item['tvshowid']==playedTvShow['tvshowid']]
                episodes = sorted(episodes, key=lambda x: [x['season'],x['episode']], reverse=False)
                if len(episodes) > 0:
                    nextEpisodes.append(episodes[0])
        return nextEpisodes[:self.ItemLimit]
        
    def _getFechOnePlaylist(self, id):
        details = self._getDetails(id)
        if details:
            if self.RealType == 'episodes':
                filepath = helper.splitPath(details['file'])
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"path","operator":"is","value":["%s"]},{"field":"filename","operator":"is","value":["%s"]}]},"type":"episodes"}' %(self.Name, filepath[0] + '/', filepath[1])
                playlistbase = 'videodb://tvshows/titles/%s/%s/?xsp=%s' %(details['tvshowid'], details['season'], urllib.quote(playlistfilter))
            elif self.RealType == 'tvshows':
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"title","operator":"is","value":["%s"]}]},"type":"tvshows"}' %(self.Name, details['showtitle'])
                playlistbase = 'videodb://tvshows/titles/?xsp=%s' %(urllib.quote(playlistfilter))
            
            return playlistbase
        return None