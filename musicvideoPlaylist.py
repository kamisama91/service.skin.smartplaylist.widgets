import random
import urllib
import helper
import videoPlaylist as vpl

class MusicVideoPlaylist(vpl.VideoPlaylist):
    def __init__(self, alias, path, name, type):
        vpl.VideoPlaylist.__init__(self, alias, path, name, type, 'musicvideo')
    
    def _set_playlist_properties(self):
        vpl.VideoPlaylist._set_playlist_properties(self)
        helper.set_property("%s.Artists" %self._alias, str(self._getArtistsCount()))
        
    def _set_one_item_properties(self, property, item):
        vpl.VideoPlaylist._set_one_item_properties(self, property, item)
        if item:
            helper.set_property("%s.Artist"  % property, '%s' %item['artist'])
            helper.set_property("%s.Art(poster)"  % property, item.get('thumbnail',''))
            helper.set_property("%s.Art(fanart)"  % property, item.get('fanart',''))

    def _clear_playlist_properties(self):
        vpl.VideoPlaylist._clear_playlist_properties(self)
        for property in ['Artists']:
            helper.clear_property('%s.%s' %(self._alias, property))
            
    def _clear_one_item_properties(self, property):
        vpl.VideoPlaylist._clear_one_item_properties(self, property)
        for item in ['Artist', 'Art(poster)', 'Art(fanart)']:
            helper.clear_property('%s.%s' %(property, item)) 
    
    def _getArtistsCount(self):
        allArtists = []
        for artists in [item.get('artist', []) for item in self._items]:
            for artist in artists:
                if artist not in allArtists:
                    allArtists.append(artist)
        return len(allArtists)
        
    def _get_item_details_fields(self):
        return vpl.VideoPlaylist._get_item_details_fields(self) + ',"dateadded", "artist", "fanart", "thumbnail"'
   
    def _get_one_item_details_from_database(self, id):
        response = helper.execute_json_rpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideoDetails", "params": {"properties": [%s], "musicvideoid":%s }, "id": 1}' %(self._get_item_details_fields(), id))
        details = response.get( 'result', {} ).get( 'musicvideodetails', None )
        if details:
            details['id'] = details['musicvideoid']
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
        
    def _get_fech_one_item_directory_source(self, details):
        if details:
            filepath = helper.split_path(details['file'])            
            playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"path","operator":"is","value":["%s"]},{"field":"filename","operator":"is","value":["%s"]}]},"type":"musicvideos"}' %(self.playlistName, filepath[0], filepath[1])
            playlistbase = 'videodb://musicvideos/titles/?xsp=%s' %urllib.quote(playlistfilter)
            return playlistbase
        return None
