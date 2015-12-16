import os
import sys
import xbmc
import xbmcaddon
import random
from xml.dom.minidom import parse
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
from playlist import Playlist

__addon__        = xbmcaddon.Addon()
__addonpath__    = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')


class EpisodePlaylist(Playlist):
    
    def __init__(self, alias, path, name):
        Playlist.__init__(self, alias, path, name, 'episode')
        
    def SetPlaylistProperties(self):
        Playlist.SetPlaylistProperties(self)
        self._setProperty("%s.TvShows" %self.Alias, str(self._getTvShowCount()))
    
    def _getTvShowCount(self):
        showIds = set([item['tvshowid'] for item in self.Items])
        return len(showIds)
        
    def _fetchAllItems(self):
        return self._fetchAllFromDirectory(self.Path)
        
    def _fetchAllFromDirectory(self, directory):
        _result = []
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "video", "properties": ["title", "tvshowid", "showtitle", "season", "episode", "art", "dateadded", "playcount", "lastplayed"]}, "id": 1}' %(directory))
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
                    directoryFiles = self._fetchAllFromDirectory(_file['file'])
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
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "tvshowid": %s, "properties": ["file", "title", "tvshowid", "showtitle", "season", "episode", "art", "dateadded", "playcount", "lastplayed"] }, "id": 1}' %(tvShowId))
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

    def _fetchOneItem(self, id):
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": ["showtitle", "season", "episode"], "movieid":%s }, "id": 1}' %id)
        _json_query = unicode(_json_query, 'utf-8', errors='ignore')
        _json_set_response = simplejson.loads(_json_query)
        details = _json_set_response.get( 'result', {} ).get( 'episodedetails', None )
        if details:
            fetchPlaylist = self._createFechOnePlaylist(id, details['showtitle'], details['season'], details['episode'])
            result = self._fetchAllFromDirectory(fetchPlaylist)
            os.remove(xbmc.translatePath(fetchPlaylist))
            for file in result:
                if file['id'] == id:
                    return file
        return None
    
    def _createFechOnePlaylist(self, id, showtitle, season, episode):
        # Load template
        _templatepath = '%s/resources/playlists/fetchoneepisode.xsp' %(__addonpath__)
        _template = parse(_templatepath)
        # Set name
        _searchPlylistName = 'searchPlaylist'
        for node in _template.getElementsByTagName('name'):
            if '{PLAYLIST_NAME}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{PLAYLIST_NAME}', self.Name)
            if '{EPISODE_ID}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{EPISODE_ID}', '%s' %id)
            _searchPlylistName = node.firstChild.nodeValue
        # Set source playlist
        for node in _template.getElementsByTagName('value'):
            if '{PLAYLIST_NAME}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{PLAYLIST_NAME}', self.Name)
            if '{EPISODE_TVSHOW}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{EPISODE_TVSHOW}', showtitle)
            if '{EPISODE_SEASON}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{EPISODE_SEASON}', season)
            if '{EPISODE_EPISODE}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{EPISODE_EPISODE}', episode)
        # Save formatedPlaylist
        _path = '%s%s.xsp' %(xbmc.translatePath('special://profile/playlists/video/'), _searchPlylistName)
        _file =  open(_path, 'wb')
        _template.writexml(_file)
        _file.close()
        return _path.replace(xbmc.translatePath('special://profile/'), 'special://profile/').replace('\\', '/')
        
    def _getRandomItems(self):
        items = [item for item in self.Items if item['season']>0] if __addon__.getSetting("ignore_specials") == 'true' else [item for item in self.Items]
        items = [item for item in items if item['playcount']==0] if __addon__.getSetting("random_unplayed") == 'true' else [item for item in items]
        random.shuffle(items)
        return items[:int(__addon__.getSetting("nb_item"))]
        
    def _getRecentItems(self):
        items = [item for item in self.Items if item['season']>0] if __addon__.getSetting("ignore_specials") == 'true' else [item for item in self.Items]
        items = [item for item in items if item['playcount']==0] if __addon__.getSetting("recent_unplayed") == 'true' else [item for item in items]
        items = sorted(items, key=lambda x: x['dateadded'], reverse=True)
        return items[:int(__addon__.getSetting("nb_item"))]
        
    def _getSuggestedItems(self):
        playedTvShows = []
        playedTvShowIds = set([item['tvshowid'] for item in self.Items if item['playcount']>0])        
        for playedTvShowId in playedTvShowIds:
            lastPlayed = max([item['lastplayed'] for item in self.Items if item['playcount']>0 and item['tvshowid']==playedTvShowId])
            playedTvShows.append({'tvshowid':playedTvShowId, 'lastplayed':lastPlayed})
        nextEpisodes = []
        playedTvShows = sorted(playedTvShows, key=lambda x: x['lastplayed'], reverse=True)
        for playedTvShow in playedTvShows:
            episodes = [item for item in self.Items if item['playcount']==0 and item['season']>0 and item['tvshowid']==playedTvShow['tvshowid']]
            episodes = sorted(episodes, key=lambda x: [x['season'],x['episode']], reverse=False)
            if len(episodes) > 0:
                nextEpisodes.append(episodes[0])
        return nextEpisodes[:int(__addon__.getSetting("nb_item"))]
        
    def _setOnePlaylistItemsProperties(self, property, item):
        if item:
            self._setProperty("%s.DBID"         % property, str(item.get('id')))
            self._setProperty("%s.Title"        % property, item.get('title'))
            self._setProperty("%s.EpisodeNo"    % property, "S%.2dE%.2d" %(float(item.get('season')), float(item.get('episode'))))
            self._setProperty("%s.TVshowTitle"  % property, item.get('showtitle'))
            self._setProperty("%s.Art(thumb)"   % property, item['art'].get('thumb',''))
            self._setProperty("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))
            self._setProperty("%s.File"         % property, item.get('file',''))
        else:
            self._setProperty("%s.Title"        % property, '')