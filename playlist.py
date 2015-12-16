import xbmc
import xbmcaddon
import xbmcgui

__addon__        = xbmcaddon.Addon()
__addonpath__    = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')

class Playlist():

    def _logNotification(self, obj):
        message = '%s (%s) : %s' % (self.Name, self.Type, obj)
        file = open(__addonpath__ + "/notification.log", "a")
        file.write(message + '\r\n')
        file.close()
    
    def _setProperty ( self, _property, _value ):
        xbmcgui.Window( 10000 ).setProperty ( _property, _value )
        #self._logNotification('Set property: %s = %s' %(_property, _value.encode('ascii', 'ignore')))
    
    def __init__(self, alias, path, name, type):
        self.Path = path
        self.Alias = alias
        self.Name = name
        self.Type = type
        self.Items = []
        self.WatchedItems = []        
        items = self._fetchAllItems()
        if items:
            self.Items = items
            self.WatchedItems = [item['id'] for item in self.Items if item['playcount']>0]          
        
    def AddItem(self, id):
        if len([item for item in self.Items if item['id']==id]) == 0:
            item = self._fetchOneItem(id)
            if item:
                self._logNotification('Added %s' %id)
                self.Items.append(item)
        
    def RemoveItem(self, id):
        items = [item for item in self.Items if item['id']==id]
        for item in items:
            self._logNotification('Removed %s' %id)
            self.Items.remove(item)
        self.SetUnWatched(id)
                
    def SetWatched(self, id):
        if len([item for item in self.Items if item['id']==id]) > 0 and len([item for item in self.WatchedItems if item==id]) == 0:
            self._logNotification('Watched %s' %id)
            self.WatchedItems.append(id)
            
    def SetUnWatched(self, id):
        watchedIds = [item for item in self.WatchedItems if item==id]
        for watchedId in watchedIds:
            self._logNotification('Unwatched %s' %id)
            self.WatchedItems.remove(watchedId)
    
    def SetPlaylistProperties(self):
        self._setProperty("%s.Name"       %self.Alias, self.Name)
        self._setProperty("%s.Type"       %self.Alias, self.Type)
        self._setProperty("%s.Count"      %self.Alias, str(self._getItemCount()))
        self._setProperty("%s.Watched"    %self.Alias, str(self._getWatchedItemCount()))
        self._setProperty("%s.Unwatched"  %self.Alias, str(self._getUnwatchedItemCount()))

    def _getItemCount(self):
        return len(self.Items)
        
    def _getWatchedItemCount(self):
        return len(self.WatchedItems)
        
    def _getUnwatchedItemCount(self):
        return self._getItemCount() - self._getWatchedItemCount() 

    def RefreshItems(self, mode):
        items = None
        if mode in ['Suggested', 'Recommended']:
            items = self._getSuggestedItems()
        elif mode in ['Recent', 'Last']:
            items = self._getRecentItems()
        else:
            items = self._getRandomItems()
        self._setAllPlaylistItemsProperties(mode, items)
             
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
        while count <= 20:
            property = '%s#%s.%s' %(self.Alias, mode, count)
            self._setOnePlaylistItemsProperties(property, None)
            count += 1
            
    def _setOnePlaylistItemsProperties(self, property, item):
        return None
                   
    def _fetchAllItems(self):
        return None
    
    def _fetchOneItem(self, id):
        return None