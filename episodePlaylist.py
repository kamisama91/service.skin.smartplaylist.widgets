import random
import urllib
import helper
import playlist as pl

class EpisodePlaylist(pl.Playlist):
    def __init__(self, alias, path, name, type):
        pl.Playlist.__init__(self, alias, path, name, 'episode')
        self.__realType = type
        self.__ignoreSpecials = False

    def _read_settings(self, settings):
        pl.Playlist._read_settings(self, settings)
        if settings:
            self.__ignoreSpecials = settings.getSetting("ignore_specials") == 'true'
            
    def _set_playlist_properties(self):
        pl.Playlist._set_playlist_properties(self)
        helper.set_property("%s.TvShows" %self._alias, str(self._getTvShowCount()))
    
    def _set_one_item_properties(self, property, item):
        pl.Playlist._set_one_item_properties(self, property, item)
        if item:
            helper.set_property("%s.EpisodeNo"    % property, "S%.2dE%.2d" %(float(item.get('season')), float(item.get('episode'))))
            helper.set_property("%s.TVshowTitle"  % property, item.get('showtitle'))
            helper.set_property("%s.Art(thumb)"   % property, item['art'].get('thumb',''))
            helper.set_property("%s.Art(fanart)"  % property, item['art'].get('tvshow.fanart',''))
   
    def _clear_playlist_properties(self):
        pl.Playlist._clear_playlist_properties(self)
        for property in ['TvShows']:
            helper.clear_property('%s.%s' %(self._alias, property))
        
    def _clear_one_item_properties(self, property):
        pl.Playlist._clear_one_item_properties(self, property)
        for item in ['EpisodeNo', 'TVshowTitle', 'Art(thumb)', 'Art(fanart)']:
            helper.clear_property('%s.%s' %(property, item)) 
                
    def _getTvShowCount(self):
        showIds = set([item['tvshowid'] for item in self._items])
        return len(showIds)

    def _get_item_details_fields(self):
        return pl.Playlist._get_item_details_fields(self) + ', "tvshowid", "showtitle", "season", "episode"'

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
        playedTvShows = []
        playedTvShowIds = set([item['tvshowid'] for item in self._items if item['playcount']>0])      
        for playedTvShowId in playedTvShowIds:
            lastPlayed = max([item['lastplayed'] for item in self._items if item['tvshowid']==playedTvShowId])
            playedTvShows.append({'tvshowid':playedTvShowId, 'lastplayed':lastPlayed})
        nextEpisodes = []
        playedTvShows = sorted(playedTvShows, key=lambda x: x['lastplayed'], reverse=True)
        for playedTvShow in playedTvShows:
            episodes = [item for item in self._items if item['playcount']==0 and item['season']>0 and item['tvshowid']==playedTvShow['tvshowid']]
            episodes = sorted(episodes, key=lambda x: [x['season'],x['episode']], reverse=False)
            if len(episodes) > 0:
                nextEpisodes.append(episodes[0])
            elif not self.__ignoreSpecials:
                episodes = [item for item in self._items if item['playcount']==0 and item['season']==0 and item['tvshowid']==playedTvShow['tvshowid']]
                episodes = sorted(episodes, key=lambda x: [x['season'],x['episode']], reverse=False)
                if len(episodes) > 0:
                    nextEpisodes.append(episodes[0])
        return nextEpisodes[:self._itemLimit]
        
    def _get_fech_one_item_video_source(self, details):
        if details:
            if self.__realType == 'episodes':
                filepath = helper.split_path(details['file'])
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"path","operator":"is","value":["%s"]},{"field":"filename","operator":"is","value":["%s"]}]},"type":"episodes"}' %(self.name, filepath[0] + '/', filepath[1])
                playlistbase = 'videodb://tvshows/titles/%s/%s/?xsp=%s' %(details['tvshowid'], details['season'], urllib.quote(playlistfilter))
            elif self.__realType == 'tvshows':
                playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"title","operator":"is","value":["%s"]}]},"type":"tvshows"}' %(self.name, details['showtitle'])
                playlistbase = 'videodb://tvshows/titles/?xsp=%s' %(urllib.quote(playlistfilter))
            return playlistbase
        return None