import time
import os
import xbmc
import xbmcaddon
import xbmcgui
from xml.dom.minidom import parse

__addon__        = xbmcaddon.Addon()
__addonpath__    = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')

class Playlist():

    def _setProperty ( self, _property, _value ):
        xbmcgui.Window( 10000 ).setProperty ( _property, _value )
    
    def __init__(self, alias, path, name, type):
        self.Path = path
        self.Alias = alias
        self.Name = name
        self.Type = type
        self.Items = []  
        items = self._fetchAllItems()
        if items:
            self.Items = items
        
    def AddItem(self, id):
        if len([item for item in self.Items if item['id']==id]) == 0:
            item = self._fetchOneItem(id)
            if item:
                self.Items.append(item)
        
    def RemoveItem(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            self.Items.remove(item)
                
    def SetWatched(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            item['playcount'] = 1
            item['resume']['position'] = 0  #Flag as not started
            item['lastplayed'] = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(time.time()))            

    def SetUnWatched(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            item['playcount'] = 0
    
    def StartPlaying(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            item['lastplayed'] = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            item['resume']['position'] = 1  #Flag as started
    
    def GetPlaycountFromDatabase(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            details = self._getDetails(id)
            if details:
                return details['playcount']
        return 0

    def SetPlaylistProperties(self):
        self._setProperty("%s.Name"       %self.Alias, self.Name)
        self._setProperty("%s.Type"       %self.Alias, self.Type)
        self._setProperty("%s.Count"      %self.Alias, str(self._getItemCount()))
        self._setProperty("%s.Watched"    %self.Alias, str(self._getWatchedItemCount()))
        self._setProperty("%s.Unwatched"  %self.Alias, str(self._getUnwatchedItemCount()))

    def _getItemCount(self):
        return len(self.Items)
        
    def _getWatchedItemCount(self):
        return len([item for item in self.Items if item['playcount']>0])
        
    def _getUnwatchedItemCount(self):
        return self._getItemCount() - self._getWatchedItemCount() 

    def RefreshItems(self, mode):
        items = None
        if mode in ['Suggested'] and __addon__.getSetting("suggested_enable") == 'true':
            items = self._getSuggestedItems()
        elif mode in ['Recent'] and __addon__.getSetting("recent_enable") == 'true':
            items = self._getRecentItems()
        elif mode in ['Random'] and __addon__.getSetting("random_enable") == 'true':
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
        return self._fetchFromPlaylist(self.Path)
    
    def _fetchOneItem(self, id):
        details = self._getDetails(id)
        if details:
            fetchPlaylist = self._createFechOnePlaylist(id, details['file'])
            result = self._fetchFromPlaylist(fetchPlaylist)
            os.remove(xbmc.translatePath(fetchPlaylist))
            for file in result:
                if file['id'] == id:
                    return file
        return None

    def _getDetails(self, id):
        return None
    
    def _fetchFromPlaylist(self, directory):
        return None
        
    def _createFechOnePlaylist(self, fileId, fullpath):
        filePath = os.path.split(fullpath)
        # Load template
        _templatepath = '%s/resources/playlists/fetchone.xsp' %(__addonpath__)
        _template = parse(_templatepath)
        # Set name
        _searchPlaylistName = 'searchPlaylist'
        if '{PLALIST_TYPE}' in _template.getElementsByTagName('smartplaylist')[0].attributes.item(0).value:
            _template.getElementsByTagName('smartplaylist')[0].attributes.item(0).value = _template.getElementsByTagName('smartplaylist')[0].attributes.item(0).value.replace('{PLALIST_TYPE}', self.Type + 's')
        for node in _template.getElementsByTagName('name'):
            if '{PLAYLIST_NAME}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{PLAYLIST_NAME}', self.Name)
            if '{FILE_ID}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{FILE_ID}', str(fileId))
            _searchPlaylistName = node.firstChild.nodeValue
        # Set source playlist
        for node in _template.getElementsByTagName('value'):
            if '{PLAYLIST_NAME}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{PLAYLIST_NAME}', self.Name)
            if '{FILE_PATH}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{FILE_PATH}', filePath[0] + '/')
            if '{FILE_NAME}' in node.firstChild.nodeValue:
                node.firstChild.nodeValue = node.firstChild.nodeValue.replace('{FILE_NAME}', filePath[1])
        # Save formatedPlaylist
        _path = '%s%s.xsp' %(xbmc.translatePath('special://profile/playlists/video/'), _searchPlaylistName)
        _file =  open(_path, 'wb')
        _template.writexml(_file)
        _file.close()
        return _path.replace(xbmc.translatePath('special://profile/'), 'special://profile/').replace('\\', '/') 
