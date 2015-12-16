import os
import sys
import xbmc
import xbmcaddon
import random
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
from playlist import Playlist

class EpisodePlaylist(Playlist):
    
    def __init__(self, alias, path, name):
        Playlist.__init__(self, alias, path, name, 'episode')
        
    def _setPlaylistProperties(self):
        Playlist._setPlaylistProperties(self)
        self._setProperty("%s.TvShows" %self.Alias, str(self._getTvShowCount()))
    
    def _setOnePlaylistItemsProperties(self, property, item):
        Playlist._setOnePlaylistItemsProperties(self, property, item)
        if item:
            self._setProperty("%s.EpisodeNo"    % property, "S%.2dE%.2d" %(float(item.get('season')), float(item.get('episode'))))
            self._setProperty("%s.TVshowTitle"  % property, item.get('showtitle'))
            self._setProperty("%s.Art(thumb)"   % property, item['art'].get('thumb',''))
            self._setProperty("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))
   
    def _clearPlaylistProperties(self):
        Playlist._clearPlaylistProperties(self)
        for property in ['Name', 'Type', 'Count', 'Watched', 'Unwatched']:
            self._clearProperty('%s.%s' %(self.Alias, property))
        
    def ClearOnePlaylistItemsProperties(self, property):
        Playlist.ClearOnePlaylistItemsProperties(self, property)
        for item in ['EpisodeNo', 'TVshowTitle', 'Art(thumb)', 'Art(fanart)']:
            self._clearProperty('%s.%s' %(property, item)) 
                
    def _getTvShowCount(self):
        showIds = set([item['tvshowid'] for item in self.Items])
        return len(showIds)
        
    def _fetchFromPlaylist(self, directory):
        _result = []
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "video", "properties": ["title", "tvshowid", "showtitle", "season", "episode", "art", "dateadded", "playcount", "lastplayed", "resume"]}, "id": 1}' %(directory))
        _json_query = unicode(_json_query, 'utf-8', errors='ignore')
        _json_set_response = simplejson.loads(_json_query)
        _files = _json_set_response.get( "result", {} ).get( "files" )
        if _files:
            for _file in _files:
                if xbmc.abortRequested:
                    break
                if _file['type'] == 'tvshow':
                    showFiles = self._fetchAllFromTvShow(_file['id'])
                    for showFile in showFiles:
                        id = showFile.get('id', -1)
                        if id != -1 and id not in [file['id'] for file in _result]:
                            _result.append(showFile)
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

    def _fetchAllFromTvShow(self, tvShowId):
        _result = []
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "tvshowid": %s, "properties": ["file", "title", "tvshowid", "showtitle", "season", "episode", "art", "dateadded", "playcount", "lastplayed", "resume"] }, "id": 1}' %(tvShowId))
        _json_query = unicode(_json_query, 'utf-8', errors='ignore')
        _json_response = simplejson.loads(_json_query)
        _files = _json_response.get( "result", {} ).get( "episodes" )
        if _files:
            for _file in _files:
                if xbmc.abortRequested:
                    break
                _file["id"] = _file['episodeid']
                _result.append(_file)
        return _result

    def _getDetails(self, id):
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": ["file", "showtitle", "season", "episode", "playcount"], "episodeid":%s }, "id": 1}' %id)
        _json_query = unicode(_json_query, 'utf-8', errors='ignore')
        _json_set_response = simplejson.loads(_json_query)
        details = _json_set_response.get( 'result', {} ).get( 'episodedetails', None )
        if details:
            details['id'] = details['episodeid']
        return details
        
    def _getRandomItems(self):
        addon = xbmcaddon.Addon()
        items = [item for item in self.Items if item['season']>0] if addon.getSetting("ignore_specials") == 'true' else [item for item in self.Items]
        items = [item for item in items if item['playcount']==0] if addon.getSetting("random_unplayed") == 'true' else [item for item in items]
        random.shuffle(items)
        return items[:int(addon.getSetting("nb_item"))]
        
    def _getRecentItems(self):
        addon = xbmcaddon.Addon()
        items = [item for item in self.Items if item['season']>0] if addon.getSetting("ignore_specials") == 'true' else [item for item in self.Items]
        items = [item for item in items if item['playcount']==0] if addon.getSetting("recent_unplayed") == 'true' else [item for item in items]
        items = sorted(items, key=lambda x: x['dateadded'], reverse=True)
        return items[:int(addon.getSetting("nb_item"))]
        
    def _getSuggestedItems(self):
        addon = xbmcaddon.Addon()
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
            elif addon.getSetting("ignore_specials") != 'true':
                episodes = [item for item in self.Items if item['playcount']==0 and item['season']==0 and item['tvshowid']==playedTvShow['tvshowid']]
                episodes = sorted(episodes, key=lambda x: [x['season'],x['episode']], reverse=False)
                if len(episodes) > 0:
                    nextEpisodes.append(episodes[0])
        return nextEpisodes[:int(addon.getSetting("nb_item"))]
        