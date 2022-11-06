import random
import urllib.parse
import helper
from settings import Settings
import playlist as pl

class MoviePlaylist(pl.Playlist):
    def __init__(self, alias, path, name, type):
        super().__init__(alias, path, name, type, 'movie')
    
    def _set_statistics_properties(self, item):
        super()._set_statistics_properties(item)
        helper.set_property("%s.Sets" %self._alias, str(str(item.get('totalset', 0))))
        
    def _set_one_item_properties(self, property, item):
        super()._set_one_item_properties(property, item)
        helper.set_property("%s.SetTitle"  % property, item.get('set'))
        helper.set_property("%s.Art(poster)"  % property, item['art'].get('poster',''))
        helper.set_property("%s.Art(fanart)"  % property, item['art'].get('fanart',''))

    def _clear_statistics_properties(self):
        super()._clear_statistics_properties()
        for property in ['Sets']:
            helper.clear_property('%s.%s' %(self._alias, property))
            
    def _clear_one_item_properties(self, property):
        super()._clear_one_item_properties(property)
        for item in ['SetTitle', 'Art(poster)', 'Art(fanart)']:
            helper.clear_property('%s.%s' %(property, item)) 
    
    def _get_statistics(self):
        tokens = { "#PLAYLIST_FILTER#": super()._get_playlist_sql_where_clause() }
        statistics = helper.execute_sql_prepared_select("movie_statistics", tokens)[0]
        return {
                "total": statistics.get('total', 0),
                "watched": statistics.get('watched', 0),
                "unwatched": statistics.get('unwatched', 0),
                "totalset": statistics.get('totalset', 0)
        }
    
    def _get_random_items(self):
        tokens = {
            "#PLAYLIST_FILTER#": super()._get_playlist_sql_where_clause(),
            "#UNWATCHED_FILTER#": ">= 0" if Settings.get_instance().randomOnlyUnplayed else "= 0",
            "#ITEM_NUMBER#": str(Settings.get_instance().itemLimit),
        }
        response = helper.execute_sql_prepared_select("movie_random", tokens)
        return self._read_sql_items(response)
    
    def _get_recent_items(self):
        tokens = {
            "#PLAYLIST_FILTER#": super()._get_playlist_sql_where_clause(),
            "#UNWATCHED_FILTER#": ">= 0" if Settings.get_instance().recentOnlyUnplayed else "= 0",
            "#ITEM_NUMBER#": str(Settings.get_instance().itemLimit),
        }
        response = helper.execute_sql_prepared_select("movie_recent", tokens)
        return self._read_sql_items(response)
    
    def _get_suggested_items(self):
        tokens = {
            "#PLAYLIST_FILTER#": super()._get_playlist_sql_where_clause(),
            "#ITEM_NUMBER#": str(Settings.get_instance().itemLimit),
        }
        response = helper.execute_sql_prepared_select("movie_suggested", tokens)
        return self._read_sql_items(response)
    
    def _read_sql_items(self, sqlResponse):
        result = []
        for row in sqlResponse:
            item = {
                "id": row['id'],
                "file": row['path'] + row['file'],
                "title": row['title'],
                "set": row['settitle'],
                "art": { "poster": row['poster'], "fanart": row['fanart'] },
            }
            result.append(item)
        return result


