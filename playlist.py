import helper

MAX_ITEM = 20

class Playlist():
    def __init__(self, alias, path, name, type):
        self.Alias = None
        self.Type = type
        self.Path = path        
        self.Name = name
        self.AddonPath = None
        self.ItemLimit = 0
        self.EnableSuggested = False
        self.EnableRecent = False
        self.RecentOnlyUnplayed = False
        self.EnableRandom = False
        self.RandomOnlyUnplayed = False
        self.RandomUpdateMethod = 0
        self.Items = self._fetchAllItems()
            
    def UpdateSettings(self, alias, settings):
        self._readSettings(settings)
        self.Alias = alias
        self.Update(['Suggested', 'Recent', 'Random'])

    def _readSettings(self, settings):
        if settings:
            self.AddonPath = helper.realPath(settings.getAddonInfo('path')).decode('utf-8')
            self.ItemLimit = min([MAX_ITEM, int(settings.getSetting("nb_item"))])
            self.EnableSuggested = settings.getSetting("suggested_enable") == 'true'
            self.EnableRecent = settings.getSetting("recent_enable") == 'true'
            self.RecentOnlyUnplayed = settings.getSetting("recent_unplayed") == 'true'
            self.EnableRandom = settings.getSetting("random_enable") == 'true'
            self.RandomOnlyUnplayed = settings.getSetting("random_unplayed") == 'true'
            self.UpdateRandom = int(settings.getSetting("random_method")) == 1
            
    def AddItem(self, id):
        if len([item for item in self.Items if item['id']==id]) == 0:
            item = self._fetchOneItem(id)
            if item:
                self.Items.append(item)
                self.Update(['Suggested', 'Recent', 'Random'] if self.UpdateRandom else ['Suggested', 'Recent'])
        
    def RemoveItem(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            self.Items.remove(item)
            self.Update(['Suggested', 'Recent', 'Random'] if self.UpdateRandom else ['Suggested', 'Recent'])
                
    def SetWatched(self, id):
        for item in [item for item in self.Items if item['id']==id and item['playcount']==0]:
            item['playcount'] = 1
            item['resume']['position'] = 0
            item['lastplayed'] = helper.currentTime()
            self.Update(['Suggested', 'Recent', 'Random'] if self.UpdateRandom else ['Suggested', 'Recent'])
                
    def SetUnWatched(self, id):
        for item in [item for item in self.Items if item['id']==id and item['playcount']>0]:
            item['playcount'] = 0
            self.Update(['Suggested', 'Recent', 'Random'] if self.UpdateRandom else ['Suggested', 'Recent'])
                
    def StartPlaying(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            item['lastplayed'] = helper.currentTime()
            item['resume']['position'] = 1
    
    def StopPlaying(self, id, isEnded):
        if isEnded == False:
            self.Update(['Suggested'])
            
    def GetPlaycountFromDatabase(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            details = self._getDetails(id)
            if details:
                return details['playcount']
        return 0

 
    def Update(self, modes):
        if self.Alias:
            self._clearPlaylistProperties()
            self._setPlaylistProperties()
            for mode in modes:
                items = None
                if mode =='Suggested' and self.EnableSuggested:
                    items = self._getSuggestedItems()
                elif mode == 'Recent' and self.EnableRecent:
                    items = self._getRecentItems()
                elif self.EnableRandom:
                    mode = 'Random'
                    items = self._getRandomItems()
                self._clearAllPlaylistItemsProperties(mode)
                self._setAllPlaylistItemsProperties(mode, items)

    def _setPlaylistProperties(self):
        helper.setProperty("%s.Name"       %self.Alias, self.Name)
        helper.setProperty("%s.Type"       %self.Alias, self.Type)
        helper.setProperty("%s.Count"      %self.Alias, str(self._getItemCount()))
        helper.setProperty("%s.Watched"    %self.Alias, str(self._getWatchedItemCount()))
        helper.setProperty("%s.Unwatched"  %self.Alias, str(self._getUnwatchedItemCount()))

    def _getItemCount(self):
        return len(self.Items)
        
    def _getWatchedItemCount(self):
        return len([item for item in self.Items if item['playcount']>0])
        
    def _getUnwatchedItemCount(self):
        return self._getItemCount() - self._getWatchedItemCount() 
        
    def _getRandomItems(self):
        return None
        
    def _getRecentItems(self):
        return None
        
    def _getSuggestedItems(self):
        return None
        
    def _setAllPlaylistItemsProperties(self, mode, items):
        count = 1
        if items:
            for item in items:
                property = '%s#%s.%s' %(self.Alias, mode, count)
                self._setOnePlaylistItemsProperties(property, item)
                count = count + 1
            
    def _setOnePlaylistItemsProperties(self, property, item):
        if item:
            helper.setProperty("%s.DBID"         % property, str(item.get('id')))
            helper.setProperty("%s.Title"        % property, item.get('title'))
            helper.setProperty("%s.File"         % property, item.get('file',''))
        else:
            helper.setProperty("%s.Title"        % property, '')


    def Clean(self):
        if self.Alias:
            self._clearPlaylistProperties()
            for mode in ['Random', 'Recent', 'Suggested']:
                self._clearAllPlaylistItemsProperties(mode)
        
    def _clearPlaylistProperties(self):
        for property in ['Name', 'Type', 'Count', 'Watched', 'Unwatched']:
            helper.clearProperty('%s.%s' %(self.Alias, property))
        
    def _clearAllPlaylistItemsProperties(self, mode):        
        count = 1
        while count <= MAX_ITEM:
            property = '%s#%s.%s' %(self.Alias, mode, count)
            self._clearOnePlaylistItemsProperties(property)
            count += 1
    
    def _clearOnePlaylistItemsProperties(self, property):
        for item in ['DBID', 'Title', 'File']:
            helper.clearProperty('%s.%s' %(property, item))


    def _fetchAllItems(self):
        return self._fetchFromPlaylist(self.Path)
    
    def _fetchFromPlaylist(self, directory):
        return None
    
    def _fetchOneItem(self, id):
        fetchPlaylist = self._getFechOnePlaylist(id)
        if fetchPlaylist:
            result = self._fetchFromPlaylist(fetchPlaylist)
            for file in result:
                if file['id'] == id:
                    return file
        return None

    def _getDetails(self, id):
        return None
  
    def _getFechOnePlaylist(self, fileId):
        return None
