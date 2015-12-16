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

__addon__        = xbmcaddon.Addon()
__addonpath__    = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')


class MoviePlaylist(Playlist):

    def __init__(self, alias, path, name):
        Playlist.__init__(self, alias, path, name, 'movie')

    def _fetchFromPlaylist(self, directory):
        _result = []
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "video", "properties": ["title", "art", "dateadded", "playcount", "lastplayed", "resume"]}, "id": 1}' %(directory))
        _json_query = unicode(_json_query, 'utf-8', errors='ignore')
        _json_set_response = simplejson.loads(_json_query)
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
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["file", "title", "playcount"], "movieid":%s }, "id": 1}' %id)
        _json_query = unicode(_json_query, 'utf-8', errors='ignore')
        _json_set_response = simplejson.loads(_json_query)
        details = _json_set_response.get( 'result', {} ).get( 'moviedetails', None )
        if details:
            details['id'] = details['movieid']
        return details
    
    def _getRandomItems(self):
        items = [item for item in self.Items if item['playcount']==0] if __addon__.getSetting("random_unplayed") == 'true' else [item for item in self.Items]
        random.shuffle(items)
        return items[:int(__addon__.getSetting("nb_item"))]
        
    def _getRecentItems(self):
        items = [item for item in self.Items if item['playcount']==0] if __addon__.getSetting("recent_unplayed") == 'true' else [item for item in self.Items]
        items = sorted(items, key=lambda x: x['dateadded'], reverse=True)
        return items[:int(__addon__.getSetting("nb_item"))]
        
    def _getSuggestedItems(self):
        items = [item for item in self.Items if item['playcount']==0]
        startedItems = [item for item in items if item['resume']['position']>0]
        startedItems = sorted(startedItems, key=lambda x: x['lastplayed'], reverse=True)
        otherItems = [item for item in items if item not in startedItems]
        otherItems = sorted(otherItems, key=lambda x: x['dateadded'], reverse=True)
        items = startedItems + otherItems
        return items[:int(__addon__.getSetting("nb_item"))]
                
    def _setOnePlaylistItemsProperties(self, property, item):
        if item:
            self._setProperty("%s.DBID"         % property, str(item.get('id')))
            self._setProperty("%s.Title"        % property, item.get('title'))
            self._setProperty("%s.Art(poster)"  % property, item['art'].get('poster',''))
            self._setProperty("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))
            self._setProperty("%s.File"         % property, item.get('file',''))
        else:
            self._setProperty("%s.Title"        % property, '')