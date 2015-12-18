import xbmc
import random
import helper
import urllib
import playlist as pl

class MoviePlaylist(pl.Playlist):
    def __init__(self, alias, path, name):
        pl.Playlist.__init__(self, alias, path, name, 'movie')
    
    def _setOnePlaylistItemsProperties(self, property, item):
        pl.Playlist._setOnePlaylistItemsProperties(self, property, item)
        if item:
            helper.setProperty("%s.Art(poster)"  % property, item['art'].get('poster',''))
            helper.setProperty("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))

    def ClearOnePlaylistItemsProperties(self, property):
        pl.Playlist.ClearOnePlaylistItemsProperties(self, property)
        for item in ['Art(poster)', 'Art(fanart)']:
            helper.clearProperty('%s.%s' %(property, item)) 
            
    def _fetchFromPlaylist(self, directory):
        _result = []
        _json_set_response = helper.executeJsonRpc('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "video", "properties": ["title", "art", "dateadded", "playcount", "lastplayed", "resume"]}, "id": 1}' %(directory))
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
        _json_set_response = helper.executeJsonRpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["file", "title", "playcount"], "movieid":%s }, "id": 1}' %id)
        details = _json_set_response.get( 'result', {} ).get( 'moviedetails', None )
        if details:
            details['id'] = details['movieid']
        return details
    
    def _getRandomItems(self):
        items = [item for item in self.Items if item['playcount']==0] if self.RandomOnlyUnplayed else [item for item in self.Items]
        random.shuffle(items)
        return items[:self.ItemLimit]
        
    def _getRecentItems(self):
        items = [item for item in self.Items if item['playcount']==0] if self.RecentOnlyUnplayed else [item for item in self.Items]
        items = sorted(items, key=lambda x: x['dateadded'], reverse=True)
        return items[:self.ItemLimit]
        
    def _getSuggestedItems(self):
        items = [item for item in self.Items if item['playcount']==0]
        startedItems = [item for item in items if item['resume']['position']>0]
        startedItems = sorted(startedItems, key=lambda x: x['lastplayed'], reverse=True)
        otherItems = [item for item in items if item not in startedItems]
        otherItems = sorted(otherItems, key=lambda x: x['dateadded'], reverse=True)
        items = startedItems + otherItems
        return items[:self.ItemLimit]

    def _getFechOnePlaylist(self, id):
        details = self._getDetails(id)
        if details:
            filepath = helper.splitPath(details['file'])
            playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"path","operator":"is","value":["%s"]},{"field":"filename","operator":"is","value":["%s"]}]},"type":"movies"}' %(self.Name, filepath[0] + '/', filepath[1])
            playlistbase = 'videodb://movies/titles/?xsp=%s' %urllib.quote(playlistfilter)
            return playlistbase
        return None

