import time
import os
import xbmc
import xbmcaddon
import xbmcgui
from xml.dom.minidom import parse

MAX_ITEM = 20

class Playlist():
        
    def _setProperty ( self, _property, _value ):
        xbmcgui.Window( 10000 ).setProperty(_property, _value)
    
    def _clearProperty(self, _property):
        xbmcgui.Window( 10000 ).clearProperty(_property)
 
 
    def __init__(self, alias, path, name, type):
        self.Alias = None
        self.Path = path        
        self.Name = name
        self.Type = type
        self.Items = self._fetchAllItems()
        self.SetAlias(alias)
            
    def SetAlias(self, alias):
        if self.Alias != alias:
            if self.Alias:
                self.Clean()
            self.Alias = alias
        if self.Alias:
            self.Update(['Suggested', 'Recent', 'Random'])

            
    def AddItem(self, id):
        if len([item for item in self.Items if item['id']==id]) == 0:
            item = self._fetchOneItem(id)
            if item:
                self.Items.append(item)
                self.Update(['Suggested', 'Recent', 'Random'] if int(xbmcaddon.Addon().getSetting("random_method")) == 1 else ['Suggested', 'Recent'])
        
    def RemoveItem(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            self.Items.remove(item)
            self.Update(['Suggested', 'Recent', 'Random'] if int(xbmcaddon.Addon().getSetting("random_method")) == 1 else ['Suggested', 'Recent'])
                
    def SetWatched(self, id):
        for item in [item for item in self.Items if item['id']==id and item['playcount']==0]:
            item['playcount'] = 1
            item['resume']['position'] = 0  #Flag as not started
            item['lastplayed'] = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            self.Update(['Suggested', 'Recent', 'Random'] if int(xbmcaddon.Addon().getSetting("random_method")) == 1 else ['Suggested', 'Recent'])
                
    def SetUnWatched(self, id):
        for item in [item for item in self.Items if item['id']==id and item['playcount']>0]:
            item['playcount'] = 0
            self.Update(['Suggested', 'Recent', 'Random'] if int(xbmcaddon.Addon().getSetting("random_method")) == 1 else ['Suggested', 'Recent'])
                
    def StartPlaying(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            item['lastplayed'] = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            item['resume']['position'] = 1  #Flag as started
    
    def StopPlaying(self, id, isEnded):
        if isEnded == False:
            self.Update(['Suggested']) #Suggested depend on lastplayed/resume.position set when StartPlaying
            
    def GetPlaycountFromDatabase(self, id):
        for item in [item for item in self.Items if item['id']==id]:
            details = self._getDetails(id)
            if details:
                return details['playcount']
        return 0

 
    def Update(self, modes):
        self._setPlaylistProperties()
        for mode in modes:
            items = None
            if mode =='Suggested' and xbmcaddon.Addon().getSetting("suggested_enable") == 'true':
                items = self._getSuggestedItems()
            elif mode == 'Recent' and xbmcaddon.Addon().getSetting("recent_enable") == 'true':
                items = self._getRecentItems()
            elif mode == 'Random' and xbmcaddon.Addon().getSetting("random_enable") == 'true':
                items = self._getRandomItems()
            self._setAllPlaylistItemsProperties(mode, items)

    def _setPlaylistProperties(self):
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
        while count <= MAX_ITEM:
            property = '%s#%s.%s' %(self.Alias, mode, count)
            self._setOnePlaylistItemsProperties(property, None)
            count += 1
            
    def _setOnePlaylistItemsProperties(self, property, item):
        if item:
            self._setProperty("%s.DBID"         % property, str(item.get('id')))
            self._setProperty("%s.Title"        % property, item.get('title'))
            self._setProperty("%s.File"         % property, item.get('file',''))
        else:
            self._setProperty("%s.Title"        % property, '')


    def Clean(self):
        self._clearPlaylistProperties()
        for mode in ['Random', 'Recent', 'Suggested']:
            self._clearAllPlaylistItemsProperties(mode)
        
    def _clearPlaylistProperties(self):
        for property in ['Name', 'Type', 'Count', 'Watched', 'Unwatched']:
            self._clearProperty('%s.%s' %(self.Alias, property))
        
    def _clearAllPlaylistItemsProperties(self, mode):        
        for mode in ['Random', 'Recent', 'Suggested']:
            count = 1
            while count <= MAX_ITEM:
                property = '%s#%s.%s' %(self.Alias, mode, count)
                self._clearOnePlaylistItemsProperties(property)
                count += 1
    
    def _clearOnePlaylistItemsProperties(self, property):
        for item in ['DBID', 'Title', 'File']:
            self._clearProperty('%s.%s' %(property, item))


    def _fetchAllItems(self):
        return self._fetchFromPlaylist(self.Path)
    
    def _fetchFromPlaylist(self, directory):
        return None
    
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
  
    def _createFechOnePlaylist(self, fileId, fullpath):
        filePath = os.path.split(fullpath)
        # Load template
        _templatepath = '%s/resources/playlists/fetchone.xsp' %(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8'))
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
