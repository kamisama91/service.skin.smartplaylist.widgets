import random
import urllib.parse
import helper
from settings import Settings
import playlist as pl

class EpisodePlaylist(pl.Playlist):
    def __init__(self, alias, path, name, type):
        super().__init__(alias, path, name, type, 'episode')
    
    def _set_statistics_properties(self, item):
        super()._set_statistics_properties(item)
        helper.set_property("%s.TvShows" %self._alias, str(item.get('totaltvshow', 0)))
    
    def _set_one_item_properties(self, property, item):
        super()._set_one_item_properties(property, item)
        helper.set_property("%s.EpisodeNo"    % property, "S%.2dE%.2d" %(float(item.get('season')), float(item.get('episode'))))
        helper.set_property("%s.TVshowTitle"  % property, str(item.get('showtitle')))
        helper.set_property("%s.Art(thumb)"   % property, str(item['art'].get('thumb','')))
        helper.set_property("%s.Art(fanart)"  % property, str(item['art'].get('tvshow.fanart','')))
   
    def _clear_statistics_properties(self):
        super()._clear_statistics_properties()
        for property in ['TvShows']:
            helper.clear_property('%s.%s' %(self._alias, property))
        
    def _clear_one_item_properties(self, property):
        super()._clear_one_item_properties(property)
        for item in ['EpisodeNo', 'TVshowTitle', 'Art(thumb)', 'Art(fanart)']:
            helper.clear_property('%s.%s' %(property, item)) 
    
    def _get_statistics(self):
        tokens = { "#PLAYLIST_FILTER#": super()._get_playlist_sql_where_clause() }
        statistics = helper.execute_sql_prepared_select("video", "episode_statistics", tokens)[0]
        return {
                "total": statistics.get('total', 0),
                "watched": statistics.get('watched', 0),
                "unwatched": statistics.get('unwatched', 0),
                "totaltvshow": statistics.get('totaltvshow', 0)
        }
    
    def _get_random_items(self):
        tokens = {
            "#PLAYLIST_FILTER#": super()._get_playlist_sql_where_clause(),
            "#SPECIAL_FILTER#": "> 0" if Settings.get_instance().ignoreSpecials else  ">= 0",
            "#UNWATCHED_FILTER#": "= 0" if Settings.get_instance().randomOnlyUnplayed else ">= 0",
            "#ITEM_NUMBER#": str(Settings.get_instance().itemLimit),
        }
        response = helper.execute_sql_prepared_select("video", "episode_random", tokens)
        return self._read_sql_items(response)
    
    def _get_recent_items(self):
        tokens = {
            "#PLAYLIST_FILTER#": super()._get_playlist_sql_where_clause(),
            "#SPECIAL_FILTER#": "> 0" if Settings.get_instance().ignoreSpecials else  ">= 0",
            "#UNWATCHED_FILTER#": "= 0" if Settings.get_instance().recentOnlyUnplayed else ">= 0",
            "#ITEM_NUMBER#": str(Settings.get_instance().itemLimit),
        }
        response = helper.execute_sql_prepared_select("video", "episode_recent", tokens)
        return self._read_sql_items(response)
    
    def _get_suggested_items(self):
        tokens = {
            "#PLAYLIST_FILTER#": super()._get_playlist_sql_where_clause(),
            "#SPECIAL_FILTER#": "> 0" if Settings.get_instance().ignoreSpecials else  ">= 0",
            "#ITEM_NUMBER#": str(Settings.get_instance().itemLimit),
        }
        response = helper.execute_sql_prepared_select("video", "episode_suggested", tokens)
        return self._read_sql_items(response)
    
    def _read_sql_items(self, sqlResponse):
        result = []
        for row in sqlResponse:
            item = {
                "id": row['id'],
                "file": row['path'] + row['file'],
                "title": row['title'],
                "season": row['season'],
                "episode": row['episode'],
                "showtitle": row['tvshowtitle'],
                "art": { "thumb": row['thumb'], "tvshow.fanart":row['fanart'] },
            }
            result.append(item)
        return result
