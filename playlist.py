import xbmc
import helper

MAX_ITEM = 20

class Playlist():
    def __init__(self, alias, path, name, playlistType, itemType, mediaType):
        self._alias = alias
        self.playlistPath = path
        self.playlistName = name
        self.playlistType = playlistType        #movies/episodes/tvshows/musicvideos/songs/albums/artists/mixed
        self.itemType = itemType                #movie/episode/musicvideo/song
        self.mediaType = mediaType              #video/music/pictures/files/programs
        self._items = []
        self.__enableSuggested = False
        self.__enableRecent = False
        self.__enableRandom = False
        self._itemLimit = 0
        self._recentOnlyUnplayed = False
        self._randomOnlyUnplayed = False
        self.__randomUpdateMethod = 0
     
    def update_settings(self, alias, settings):
        self._read_settings(settings)
        self._alias = alias
        self.update(['Suggested', 'Recent', 'Random'])

    def _read_settings(self, settings):
        if settings:
            self.__enableSuggested = settings.getSetting("suggested_enable") == 'true'
            self.__enableRecent = settings.getSetting("recent_enable") == 'true'
            self.__enableRandom = settings.getSetting("random_enable") == 'true'
            self._itemLimit = min([MAX_ITEM, max([0, int(settings.getSetting("nb_item"))])])
            self._recentOnlyUnplayed = settings.getSetting("recent_unplayed") == 'true'
            self._randomOnlyUnplayed = settings.getSetting("random_unplayed") == 'true'
            self.__randomUpdateMethod = int(settings.getSetting("random_method")) == 1
    
    def reload_paylist_content(self):
        t1 = helper.current_timestamp()
        self._items = self._fetch_all_items()
        self.update(['Suggested', 'Recent', 'Random'])
        t2 = helper.current_timestamp()
        #helper.notify("%s: %d seconds" %(self.playlistName, t2-t1), 2)
     
    def contains_item(self, id):
        return len([item for item in self._items if item['id']==id]) > 0
        
    def add_item(self, id):
        if not self.contains_item(id):
            item = self._fetch_one_item(id)
            if item:
                self._items.append(item)
                self.update(['Suggested', 'Recent', 'Random'] if self.__randomUpdateMethod else ['Suggested', 'Recent'])
        
    def remove_item(self, id):
        for item in [item for item in self._items if item['id']==id]:
            self._items.remove(item)
            self.update(['Suggested', 'Recent', 'Random'])
                
    def set_watched(self, id):
        for item in [item for item in self._items if item['id']==id and item['playcount']==0]:
            item['playcount'] = 1
            item['lastplayed'] = helper.current_time()
            self.update(['Suggested', 'Recent', 'Random'] if self.__randomUpdateMethod else ['Suggested', 'Recent'])
                
    def set_unwatched(self, id):
        for item in [item for item in self._items if item['id']==id and item['playcount']>0]:
            item['playcount'] = 0
            self.update(['Suggested', 'Recent', 'Random'] if self.__randomUpdateMethod else ['Suggested', 'Recent'])
                
    def start_playing(self, id):
        for item in [item for item in self._items if item['id']==id]:
            item['lastplayed'] = helper.current_time()
    
    def stop_playing(self, id, isEnded):
        for itemFromPlaylist in [item for item in self._items if item['id']==id]:
            if isEnded == True:
                self.set_watched(itemFromPlaylist['id'])
            else:
                itemFromDatabase = None
                itemUpdatedInDatabase = False
                #Wait item update in database
                while not itemUpdatedInDatabase:
                    itemFromDatabase = self._get_one_item_details_from_database(itemFromPlaylist['id'])
                    itemUpdatedInDatabase = itemFromDatabase['lastplayed'] and (itemFromDatabase['lastplayed'] > itemFromPlaylist['lastplayed'])
                    xbmc.sleep(100)
                #Item updated then set watched or just update Suggested
                if itemFromDatabase['playcount'] > 0:
                    self.set_watched(itemFromDatabase['id'])
                else:
                    self.update(['Suggested'])
             
    def update(self, modes):
        if self._alias:
            self._set_playlist_properties()
            for mode in modes:
                items = None
                if mode =='Suggested' and self.__enableSuggested:
                    items = self._get_suggested_items()
                elif mode == 'Recent' and self.__enableRecent:
                    items = self._get_recent_items()
                elif self.__enableRandom:
                    mode = 'Random'
                    items = self._get_random_items()
                if items:
                    self.__set_all_items_properties(mode, items)
                    self._clear_all_items_Properties_from_position(mode, len(items) + 1)
                else:
                    self._clear_all_items_Properties(mode)

    def _set_playlist_properties(self):
        helper.set_property("%s.Name"       %self._alias, self.playlistName)
        helper.set_property("%s.Type"       %self._alias, self.itemType )
        helper.set_property("%s.Count"      %self._alias, str(self.__get_item_count()))
        helper.set_property("%s.Watched"    %self._alias, str(self.__get_watched_item_count()))
        helper.set_property("%s.Unwatched"  %self._alias, str(self.__get_unwatched_item_count()))

    def __get_item_count(self):
        return len(self._items)
        
    def __get_watched_item_count(self):
        return len([item for item in self._items if item['playcount']>0])
        
    def __get_unwatched_item_count(self):
        return self.__get_item_count() - self.__get_watched_item_count() 
        
    def _get_random_items(self):
        return None
        
    def _get_recent_items(self):
        return None
        
    def _get_suggested_items(self):
        return None
        
    def __set_all_items_properties(self, mode, items):
        count = 1
        if items:
            for item in items:
                property = '%s#%s.%s' %(self._alias, mode, count)
                self._set_one_item_properties(property, item)
                count = count + 1
     
    def _set_one_item_properties(self, property, item):
        if item:
            helper.set_property("%s.DBID"         % property, str(item.get('id')))
            helper.set_property("%s.File"         % property, item.get('file',''))
            helper.set_property("%s.Title"        % property, item.get('title'))
        else:
            helper.set_property("%s.Title"        % property, '')
    
    def clean(self):
        if self._alias:
            self._clear_playlist_properties()
            for mode in ['Random', 'Recent', 'Suggested']:
                self._clear_all_items_Properties(mode)
        
    def _clear_playlist_properties(self):
        for property in ['Name', 'Type', 'Count', 'Watched', 'Unwatched']:
            helper.clear_property('%s.%s' %(self._alias, property))
        
    def _clear_all_items_Properties(self, mode):        
        self._clear_all_items_Properties_from_position(mode, 1)
    
    def _clear_all_items_Properties_from_position(self, mode, position):
        count = position
        while count <= MAX_ITEM:
            property = '%s#%s.%s' %(self._alias, mode, count)
            self._clear_one_item_properties(property)
            count += 1
    
    def _clear_one_item_properties(self, property):
        for item in ['DBID', 'Title', 'File']:
            helper.clear_property('%s.%s' %(property, item))
    
    def _get_item_details_fields(self):
         return '"file", "title", "lastplayed", "playcount"'
    
    def _get_one_item_details_from_database(self, id):
        return None
    
    def _fetch_all_items(self):
        response = helper.execute_json_rpc('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "%s", "properties": [%s]}, "id": 1}' %(self.playlistPath, self.mediaType, self._get_item_details_fields()))
        files = response.get( "result", {} ).get("files", [])
        return [file for file in files if file['filetype'] != 'directory' and file.get('id', -1) != -1]
    
    def _fetch_one_item(self, id):
        item = self._get_one_item_details_from_database(id)
        return item if item and self._is_item_in_playlist(item) else None
    
    def _is_item_in_playlist(self, item):
        return False

