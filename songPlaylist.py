import random
import urllib
import helper
import audioPlaylist as apl

class SongPlaylist(apl.AudioPlaylist):
    def __init__(self, alias, path, name, type):
        apl.AudioPlaylist.__init__(self, alias, path, name, type, 'song')
 
    def _set_playlist_properties(self):
        apl.AudioPlaylist._set_playlist_properties(self)
        helper.set_property("%s.Artists" %self._alias, str(self._getArtistsCount()))
        helper.set_property("%s.Albums" %self._alias, str(self._getAlbumsCount()))
    
    def _set_one_item_properties(self, property, item):
        apl.AudioPlaylist._set_one_item_properties(self, property, item)
        if item:
            helper.set_property("%s.Artist"    % property, '%s' %item['artist'])
            helper.set_property("%s.Album"  % property, item['album'])
            helper.set_property("%s.Art(thumb)"   % property, item['thumbnail'])
            helper.set_property("%s.Art(fanart)"  % property, item['fanart'])
   
    def _clear_playlist_properties(self):
        apl.AudioPlaylist._clear_playlist_properties(self)
        for property in ['Artists', 'Albums']:
            helper.clear_property('%s.%s' %(self._alias, property))
        
    def _clear_one_item_properties(self, property):
        apl.AudioPlaylist._clear_one_item_properties(self, property)
        for item in ['Artist', 'Album', 'Art(thumb)', 'Art(fanart)']:
            helper.clear_property('%s.%s' %(property, item)) 

    def _getArtistsCount(self):
        allArtists = []
        for artists in [item.get('artist', []) for item in self._items]:
            for artist in artists:
                if artist not in allArtists:
                    allArtists.append(artist)
        return len(allArtists)
        
    def _getAlbumsCount(self):
        albumIds = set([item['albumid'] for item in self._items])
        return len(albumIds)

    def _get_item_details_fields(self):
        return apl.AudioPlaylist._get_item_details_fields(self) + ', "artistid", "artist", "albumid", "album", "thumbnail", "fanart"'

    def _get_one_item_details_from_database(self, id):
        response = helper.execute_json_rpc('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongDetails", "params": {"properties": [%s], "songid":%s }, "id": 1}' %(self._get_item_details_fields(),id))
        details = response.get( 'result', {} ).get( 'songdetails', None )
        if details:
            details['id'] = details['songid']
        return details
        
    def _get_random_items(self):
        items = [item for item in self._items if item['playcount']==0] if self._randomOnlyUnplayed else [item for item in self._items]
        random.shuffle(items)
        return items[:self._itemLimit]
        
    def _get_recent_items(self):
        items = [item for item in self._items if item['playcount']==0] if self._recentOnlyUnplayed else [item for item in self._items]
        items = sorted(items, key=lambda x: x['id'], reverse=True)
        return items[:self._itemLimit]
        
    def _get_suggested_items(self):
        return self._get_recent_items()
        
    def _get_fech_one_item_directory_source(self, details):
        if details:
            if self.playlistType == 'songs':
                filepath = helper.split_path(details['file'])
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"path","operator":"is","value":["%s"]},{"field":"filename","operator":"is","value":["%s"]}]},"type":"songs"}' %(self.playlistName, filepath[0], filepath[1])
                playlistbase = 'musicdb://songs/?xsp=%s' %(urllib.quote(playlistfilter))
            elif self.playlistType == 'albums':
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"album","operator":"is","value":["%s"]},{"field":"artist","operator":"is","value":["%s"]}]},"type":"albums"}' %(self.playlistName, details['album'], details['artist'][0])
                playlistbase = 'musicdb://albums/?xsp=%s' %(urllib.quote(playlistfilter))
            elif self.playlistType == 'artists':
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"artist","operator":"is","value":["%s"]}]},"type":"artists"}' %(self.playlistName, details['artist'][0])
                playlistbase = 'musicdb://artists/?xsp=%s' %(urllib.quote(playlistfilter))
            return playlistbase
        return None
        