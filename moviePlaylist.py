import random
import urllib
import helper
import videoPlaylist as vpl

class MoviePlaylist(vpl.VideoPlaylist):
    def __init__(self, alias, path, name, type):
        vpl.VideoPlaylist.__init__(self, alias, path, name, type, 'movie')
    
    def _set_playlist_properties(self):
        vpl.VideoPlaylist._set_playlist_properties(self)
        helper.set_property("%s.Sets" %self._alias, str(self._getSetCount()))
        
    def _set_one_item_properties(self, property, item):
        vpl.VideoPlaylist._set_one_item_properties(self, property, item)
        if item:
            helper.set_property("%s.SetTitle"  % property, item.get('set'))
            helper.set_property("%s.Art(poster)"  % property, item['art'].get('poster',''))
            helper.set_property("%s.Art(fanart)"  % property, item['art'].get('fanart',''))

    def _clear_playlist_properties(self):
        vpl.VideoPlaylist._clear_playlist_properties(self)
        for property in ['Sets']:
            helper.clear_property('%s.%s' %(self._alias, property))
            
    def _clear_one_item_properties(self, property):
        vpl.VideoPlaylist._clear_one_item_properties(self, property)
        for item in ['SetTitle', 'Art(poster)', 'Art(fanart)']:
            helper.clear_property('%s.%s' %(property, item)) 
    
    def _getSetCount(self):
        setIds = set([item['setid'] for item in self._items if item['setid']>0])
        return len(setIds)
        
    def _get_item_details_fields(self):
        return vpl.VideoPlaylist._get_item_details_fields(self) + ',"dateadded", "art", "setid", "set", "year"'
   
    def _get_one_item_details_from_database(self, id):
        response = helper.execute_json_rpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": [%s], "movieid":%s }, "id": 1}' %(self._get_item_details_fields(), id))
        details = response.get( 'result', {} ).get( 'moviedetails', None )
        if details:
            details['id'] = details['movieid']
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
        unplayedItems = [item for item in self._items if item['playcount']==0]
        #Get all started movie form last played to first played
        startedMovies = [item for item in unplayedItems if item['resume']['position']>0]
        startedMovies = sorted(startedMovies, key=lambda x: x['lastplayed'], reverse=True)
        #Then get the first movie (by year) from each set where at least one movie is played and no movie is started (selected in 1st case)
        playedSets = []
        playedSetIds = set([item['setid'] for item in self._items if item['setid']>0 and item['playcount']>0 and item['setid'] not in [startedItem['setid'] for startedItem in startedMovies]])
        for playedSetId in playedSetIds:
            #Relevent order in max(lastpayed in set set, min(date(dateadded) with palycount=0 in set set)), lastplayed 
            lastPlayed = max([item['lastplayed'] for item in self._items if item['setid']==playedSetId])
            dateAdded = "0000-00-00 00:00:00"
            setUnplayedMoviesDateAdded = [helper.date(item['dateadded']) for item in self._items if item['setid']==playedSetId and item['playcount']==0]
            if len(setUnplayedMoviesDateAdded) > 0:
                dateAdded = min(setUnplayedMoviesDateAdded)
            playedSets.append({'setid':playedSetId, 'relevantupdatedate':max([lastPlayed,dateAdded]), 'lastplayed':lastPlayed})
        playedSets = sorted(playedSets, key=lambda x: [x['relevantupdatedate'],x['lastplayed']], reverse=True)
        nextMoviesFromStartedSets = []
        for playedSet in playedSets:
            movies = [item for item in unplayedItems if item['setid']==playedSet['setid']]
            movies = sorted(movies, key=lambda x: x['year'], reverse=False)
            if len(movies) > 0:
                nextMoviesFromStartedSets.append(movies[0])
        #Then order from most recent to oldest other items: 
        # - When not in a set: not played/started movie
        otherItems = []
        for movie in [item for item in unplayedItems if item['setid']==0 and item not in startedMovies]:
            otherItems.append({'movie':movie, 'dateadded':movie['dateadded']})
        # - When is a not played/inprogress set: first not played/started movie from the set with the maximum dateadded from the set
        otherSetIds = set([item['setid'] for item in unplayedItems if item['setid']>0 and item['setid'] not in [startedItem['setid'] for startedItem in startedMovies] and item['setid'] not in playedSetIds])
        for otherSetId in otherSetIds:
            otherSetMovies = [item for item in unplayedItems if item['setid']==otherSetId]
            if len(otherSetMovies) > 0:
                otherSetMovies = sorted(otherSetMovies, key=lambda x: x['year'], reverse=False)
                otherItems.append({'movie':otherSetMovies[0], 'dateadded':max([otherSetMovie['dateadded'] for otherSetMovie in otherSetMovies])})
        otherItems = sorted(otherItems, key=lambda x: x['dateadded'], reverse=True)
        otherItems = [item['movie'] for item in otherItems]
        #Mix and limit the result
        items = startedMovies + nextMoviesFromStartedSets + otherItems
        return items[:self._itemLimit]

    def _get_fech_one_item_directory_source(self, details):
        if details:
            filepath = helper.split_path(details['file'])
            playlistfilter = '{"rules":{"and":[{"field":"playlist","operator":"is","value":["%s"]},{"field":"path","operator":"is","value":["%s"]},{"field":"filename","operator":"is","value":["%s"]}]},"type":"movies"}' %(self.playlistName, filepath[0], filepath[1])
            playlistbase = 'videodb://movies/titles/?xsp=%s' %urllib.quote(playlistfilter)
            return playlistbase
        return None

