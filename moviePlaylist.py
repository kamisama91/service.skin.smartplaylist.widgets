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


class MoviePlaylist(Playlist):

    def __init__(self, alias, path, name):
        Playlist.__init__(self, alias, path, name, 'movie')
        
    def _fetchAllItems(self):
        return self._fetchAllFromDirectory(self.Path)
        
    def _fetchAllFromDirectory(self, directory):
        _result = []
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "video", "properties": ["title", "art", "dateadded", "playcount", "lastplayed"]}, "id": 1}' %(directory))
        _json_query = unicode(_json_query, 'utf-8', errors='ignore')
        _json_set_response = simplejson.loads(_json_query)
        _files = _json_set_response.get( "result", {} ).get( "files" )
        if _files:
            for _file in _files:
                if xbmc.abortRequested:
                    break
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
            
    def _fetchOneItem(self, id):
        _json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["title"], "movieid":%s }, "id": 1}' %id)
        _json_query = unicode(_json_query, 'utf-8', errors='ignore')
        _json_set_response = simplejson.loads(_json_query)
        details = _json_set_response.get( 'result', {} ).get( 'moviedetails', None )
        if details:
            fetchPlaylist = self._createFechOnePlaylist(id, details['title'])
            result = self._fetchAllFromDirectory(fetchPlaylist)
            os.remove(xbmc.translatePath(fetchPlaylist))
            for file in result:
                if file['id'] == id:
                    return file
        return None
    
    def _createFechOnePlaylist(self, id, title):
        # Load template
        _templatepath = '%s/resources/playlists/fetchonemovie.xsp' %(__addonpath__)
        _template = parse(_templatepath)
        # Set name
        _searchPlylistName = 'searchPlaylist'
        for node in _template.getElementsByTagName('name'):
            if '{PLAYLIST_NAME}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{PLAYLIST_NAME}', self.Name)
            if '{MOVIE_ID}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{MOVIE_ID}', '%s' %id)
            _searchPlylistName = node.firstChild.nodeValue
        # Set source playlist
        for node in _template.getElementsByTagName('value'):
            if '{PLAYLIST_NAME}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{PLAYLIST_NAME}', self.Name)
            if '{MOVIE_TITLE}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{MOVIE_TITLE}', title)
        # Save formatedPlaylist
        _path = '%s%s.xsp' %(xbmc.translatePath('special://profile/playlists/video/SkinWidgetPlaylist/'), _searchPlylistName)
        _file =  open(_path, 'wb')
        _template.writexml(_file)
        _file.close()
        return _path.replace(xbmc.translatePath('special://profile/'), 'special://profile/').replace('\\', '/') 

    def _getRandomItems(self):
        items = [item for item in self.Items if item['playcount']==0]
        random.shuffle(items)
        return items[:5]
        
    def _getRecentItems(self):
        items = [item for item in self.Items if item['playcount']==0]
        items = sorted(items, key=lambda x: x['dateadded'], reverse=True)
        return items[:5]
        
    def _getSuggestedItems(self):
        items = [item for item in self.Items if item['playcount']==0]
        items = sorted(items, key=lambda x: [x['lastplayed'],x['dateadded']], reverse=True)
        return items[:5]
                
    def _setOnePlaylistItemsProperties(self, property, item):
        if item:
            self._setProperty("%s.DBID"         % property, str(item.get('id')))
            self._setProperty("%s.Title"        % property, item.get('title'))
            self._setProperty("%s.Art(poster)"  % property, item['art'].get('poster',''))
            self._setProperty("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))
            self._setProperty("%s.File"         % property, item.get('file',''))
        else:
            self._setProperty("%s.Title"        % property, '')