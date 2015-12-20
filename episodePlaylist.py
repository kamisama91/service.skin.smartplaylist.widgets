import random
import urllib
import helper
import videoPlaylist as vpl

class EpisodePlaylist(vpl.VideoPlaylist):
    def __init__(self, alias, path, name, type):
        vpl.VideoPlaylist.__init__(self, alias, path, name, type, 'episode')
        self.__ignoreSpecials = False

    def _read_settings(self, settings):
        vpl.VideoPlaylist._read_settings(self, settings)
        if settings:
            self.__ignoreSpecials = settings.getSetting("ignore_specials") == 'true'
            
    def _set_playlist_properties(self):
        vpl.VideoPlaylist._set_playlist_properties(self)
        helper.set_property("%s.TvShows" %self._alias, str(self._getTvShowCount()))
    
    def _set_one_item_properties(self, property, item):
        vpl.VideoPlaylist._set_one_item_properties(self, property, item)
        if item:
            helper.set_property("%s.EpisodeNo"    % property, "S%.2dE%.2d" %(float(item.get('season')), float(item.get('episode'))))
            helper.set_property("%s.TVshowTitle"  % property, item.get('showtitle'))
            helper.set_property("%s.Art(thumb)"   % property, item['art'].get('thumb',''))
            helper.set_property("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))
   
    def _clear_playlist_properties(self):
        vpl.VideoPlaylist._clear_playlist_properties(self)
        for property in ['TvShows']:
            helper.clear_property('%s.%s' %(self._alias, property))
        
    def _clear_one_item_properties(self, property):
        vpl.VideoPlaylist._clear_one_item_properties(self, property)
        for item in ['EpisodeNo', 'TVshowTitle', 'Art(thumb)', 'Art(fanart)']:
            helper.clear_property('%s.%s' %(property, item)) 
                
    def _getTvShowCount(self):
        showIds = set([item['tvshowid'] for item in self._items])
        return len(showIds)

    def _get_item_details_fields(self):
        return vpl.VideoPlaylist._get_item_details_fields(self) + ',"dateadded", "art", "tvshowid", "showtitle", "season", "episode"'

    def _get_one_item_details_from_database(self, id):
        response = helper.execute_json_rpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": [%s], "episodeid":%s }, "id": 1}' %(self._get_item_details_fields(),id))
        details = response.get( 'result', {} ).get( 'episodedetails', None )
        if details:
            details['id'] = details['episodeid']
        return details
        
    def _get_random_items(self):
        items = [item for item in self._items if item['season']>0] if self.__ignoreSpecials else [item for item in self._items]
        items = [item for item in items if item['playcount']==0] if self._randomOnlyUnplayed else [item for item in items]
        random.shuffle(items)
        return items[:self._itemLimit]
        
    def _get_recent_items(self):
        items = [item for item in self._items if item['season']>0] if self.__ignoreSpecials else [item for item in self._items]
        items = [item for item in items if item['playcount']==0] if self._recentOnlyUnplayed else [item for item in items]
        items = sorted(items, key=lambda x: x['dateadded'], reverse=True)
        return items[:self._itemLimit]
        
    def _get_suggested_items(self):
        playedEpisodes = [item for item in self._items if item['playcount']>0]
        if self.__ignoreSpecials:
            playedEpisodes = [item for item in playedEpisodes if item['season']>0]
        playedTvShowIds = set([item['tvshowid'] for item in playedEpisodes])      
        playedTvShows = []
        for playedTvShowId in playedTvShowIds:
            showEpisodes = [item for item in self._items if item['tvshowid']==playedTvShowId]
            if self.__ignoreSpecials:
                showEpisodes = [item for item in showEpisodes if item['season']>0]
            #Relevent order in max(lastpayed in set set, min(date(dateadded) with palycount=0 in set set)), lastplayed 
            lastPlayed = max([item['lastplayed'] for item in showEpisodes])
            dateAdded = "0000-00-00 00:00:00"
            setUnplayedEpisodesDateAdded = [helper.date(item['dateadded']) for item in showEpisodes if item['playcount']==0]
            if len(setUnplayedEpisodesDateAdded) > 0:
                dateAdded = min(setUnplayedEpisodesDateAdded)
            playedTvShows.append({'tvshowid':playedTvShowId, 'relevantupdatedate':max([lastPlayed,dateAdded]), 'lastplayed':lastPlayed})
        playedTvShows = sorted(playedTvShows, key=lambda x: [x['relevantupdatedate'],x['lastplayed']], reverse=True)       
        nextEpisodes = []
        for playedTvShow in playedTvShows:
            unplayedShowEpisodes = [item for item in self._items if item['tvshowid']==playedTvShow['tvshowid'] and item['playcount']==0]
            if self.__ignoreSpecials:
                unplayedShowEpisodes = [item for item in unplayedShowEpisodes if item['season']>0]
            unplayedShowEpisodes = sorted(unplayedShowEpisodes, key=lambda x: [x['season'],x['episode']], reverse=False)
            episodes = [item for item in unplayedShowEpisodes if item['season']>0]
            if len(episodes) > 0:
                nextEpisodes.append(episodes[0])
            else:
                episodes = episodes = [item for item in unplayedShowEpisodes if item['season']==0]
                if len(episodes) > 0:
                    nextEpisodes.append(episodes[0])
        #Then when is a not inprogress show: first not played/started episode from the show with the maximum dateadded from the show
        otherTvShowIds = set([item['tvshowid'] for item in self._items if item['tvshowid'] not in playedTvShowIds])
        firstEpisodes = []
        for otherTvShowId in otherTvShowIds:
            showEpisodes = [item for item in self._items if item['tvshowid']==otherTvShowId]            
            if self.__ignoreSpecials:
                showEpisodes = [item for item in showEpisodes if item['season']>0]
            showEpisodes = sorted(showEpisodes, key=lambda x: [x['season'],x['episode']], reverse=False)            
            dateAdded = max([item['dateadded'] for item in showEpisodes])
            episodes = [item for item in showEpisodes if item['season']>0]
            if len(episodes) > 0:
                firstEpisodes.append({'episode':episodes[0], 'dateadded':dateAdded})
            else:
                episodes = [item for item in showEpisodes if item['season']==0]
                if len(episodes) > 0:
                    firstEpisodes.append({'episode':episodes[0], 'dateadded':dateAdded})
        firstEpisodes = sorted(firstEpisodes, key=lambda x: x['dateadded'], reverse=True)
        firstEpisodes = [item['episode'] for item in firstEpisodes]
        #Mix and limit the result
        result = nextEpisodes + firstEpisodes  
        return result[:self._itemLimit]
        
    def _get_fech_one_item_directory_source(self, details):
        if details:
            if self.playlistType == 'episodes':
                filepath = helper.split_path(details['file'])
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"path","operator":"is","value":["%s"]},{"field":"filename","operator":"is","value":["%s"]}]},"type":"episodes"}' %(self.playlistName, filepath[0], filepath[1])
                playlistbase = 'videodb://tvshows/titles/%s/%s/?xsp=%s' %(details['tvshowid'], details['season'], urllib.quote(playlistfilter))
            elif self.playlistType == 'tvshows':
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"title","operator":"is","value":["%s"]}]},"type":"tvshows"}' %(self.playlistName, details['showtitle'])
                playlistbase = 'videodb://tvshows/titles/?xsp=%s' %(urllib.quote(playlistfilter))
            return playlistbase
        return None