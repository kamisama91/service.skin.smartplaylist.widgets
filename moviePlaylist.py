import random
import urllib
import helper
import playlist as pl

class MoviePlaylist(pl.Playlist):
    def __init__(self, alias, path, name):
        pl.Playlist.__init__(self, alias, path, name, 'movie')
    
    def _set_one_item_properties(self, property, item):
        pl.Playlist._set_one_item_properties(self, property, item)
        if item:
            helper.set_property("%s.Art(poster)"  % property, item['art'].get('poster',''))
            helper.set_property("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))

    def _clear_one_item_properties(self, property):
        pl.Playlist._clear_one_item_properties(self, property)
        for item in ['Art(poster)', 'Art(fanart)']:
            helper.clear_property('%s.%s' %(property, item)) 
                            
    def _get_one_item_details_from_database(self, id):
        response = helper.execute_json_rpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": [%s], "movieid":%s }, "id": 1}' %(self._get_item_details_fields(), id))
        details = response.get( 'result', {} ).get( 'moviedetails', None )
        if details:
            details['id'] = details['movieid']
        return details
    
    def _get_random_items(self):
        items = [item for item in self._items if item['playcount']==0] if self._randomOnlyUnplayed else [item for item in self._items]
        random.shuffle(items)
        return items[:self._itemLimit]
        
    def _get_recent_items(self):
        items = [item for item in self._items if item['playcount']==0] if self._recentOnlyUnplayed else [item for item in self._items]
        items = sorted(items, key=lambda x: x['dateadded'], reverse=True)
        return items[:self._itemLimit]
        
    def _get_suggested_items(self):
        items = [item for item in self._items if item['playcount']==0]
        startedItems = [item for item in items if item['resume']['position']>0]
        startedItems = sorted(startedItems, key=lambda x: x['lastplayed'], reverse=True)
        otherItems = [item for item in items if item not in startedItems]
        otherItems = sorted(otherItems, key=lambda x: x['dateadded'], reverse=True)
        items = startedItems + otherItems
        return items[:self._itemLimit]

    def _get_fech_one_item_video_source(self, details):
        if details:
            filepath = helper.split_path(details['file'])
            playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"path","operator":"is","value":["%s"]},{"field":"filename","operator":"is","value":["%s"]}]},"type":"movies"}' %(self.name, filepath[0] + '/', filepath[1])
            playlistbase = 'videodb://movies/titles/?xsp=%s' %urllib.quote(playlistfilter)
            return playlistbase
        return None

