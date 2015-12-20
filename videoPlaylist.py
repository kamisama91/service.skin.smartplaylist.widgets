import playlist as pl

class VideoPlaylist(pl.Playlist):
    def __init__(self, alias, path, name, type, itemType):
        pl.Playlist.__init__(self, alias, path, name, type, itemType, 'video')
    
    def set_watched(self, id):
        for item in [item for item in self._items if item['id']==id and item['playcount']==0]:
            item['resume']['position'] = 0
        pl.Playlist.set_watched(self, id)
    
    def start_playing(self, id):
        for item in [item for item in self._items if item['id']==id]:
            item['resume']['position'] = 1   
        pl.Playlist.start_playing(self, id)
            
    def _get_item_details_fields(self):
        return  pl.Playlist._get_item_details_fields(self) + ', "resume"'
