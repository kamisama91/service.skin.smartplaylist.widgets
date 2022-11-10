import helper
from settings import Settings

class Playlist():
    def __init__(self, alias, path, name, playlistType, itemType):
        self._alias = alias
        self.playlistPath = path
        self.playlistName = name
        self.playlistType = playlistType        #movies/episodes/tvshows
        self.itemType = itemType                #movie/episode

    def update_items(self, mode):
        self.__set_playlist_properties()
        items = []
        if mode =='Suggested':
            items = self._get_suggested_items()
        elif mode == 'Recent':
            items = self._get_recent_items()
        elif mode == 'Random':
            items = self._get_random_items()
        self.__set_all_items_properties(mode, items)
        self.__clear_all_items_Properties_from_position(mode, len(items) + 1)
        self._set_statistics_properties(self._get_statistics())
    
    def clean_items(self):
        if self._alias:
            self.__clear_playlist_properties()
            self._clear_statistics_properties()
            for mode in ['Random', 'Recent', 'Suggested']:
                self.__clear_all_items_Properties(mode)
    
    def __set_playlist_properties(self):
        helper.set_property("%s.Name"       %self._alias, str(self.playlistName))
        helper.set_property("%s.Type"       %self._alias, str(self.itemType))
    
    def __clear_playlist_properties(self):
        for property in ['Name', 'Type']:
            helper.clear_property('%s.%s' %(self._alias, property))
    
    def _set_statistics_properties(self, item):
        helper.set_property("%s.Count"      %self._alias, str(item.get('total', 0)))
        helper.set_property("%s.Watched"    %self._alias, str(item.get('watched', 0)))
        helper.set_property("%s.Unwatched"  %self._alias, str(item.get('unwatched', 0)))
    
    def _clear_statistics_properties(self):
        for property in ['Count', 'Watched', 'Unwatched']:
            helper.clear_property('%s.%s' %(self._alias, property))
    
    def __set_all_items_properties(self, mode, items):
        count = 1
        for item in items:
            property = '%s#%s.%s' %(self._alias, mode, count)
            self._set_one_item_properties(property, item)
            count += 1
    
    def _set_one_item_properties(self, property, item):
        helper.set_property("%s.DBID"         % property, str(item.get('id')))
        helper.set_property("%s.File"         % property, str(item.get('file')))
        helper.set_property("%s.Title"        % property, str(item.get('title')))
    
    def __clear_all_items_Properties(self, mode):
        self.__clear_all_items_Properties_from_position(mode, 1)
    
    def __clear_all_items_Properties_from_position(self, mode, position):
        for count in range(position, Settings.MAX_ITEM+1):
            property = '%s#%s.%s' %(self._alias, mode, count)
            self._clear_one_item_properties(property)
    
    def _clear_one_item_properties(self, property):
        for item in ['DBID', 'Title', 'File']:
            helper.clear_property('%s.%s' %(property, item))
    
    def _get_statistics(self):
        return {}
    
    def _get_random_items(self):
        return []
        
    def _get_recent_items(self):
        return []
        
    def _get_suggested_items(self):
        return []
    
    def _get_playlist_sql_where_clause (self):
        sqlWhereClauses = []
        playlistXml = helper.load_xml(self.playlistPath)
        playlistMatch = playlistXml.getElementsByTagName('match')[0].firstChild.nodeValue
        playlistRules = playlistXml.getElementsByTagName('rule')
        for playlistRule in playlistRules:
            field = playlistRule.attributes['field'].value
            operator = playlistRule.attributes['operator'].value
            value = playlistRule.getElementsByTagName('value')[0].firstChild.nodeValue
            ruleClause = self.__get_rule_sql_where_clause(field, operator, value)
            if ruleClause:
                sqlWhereClauses.append(ruleClause)
        if len(sqlWhereClauses) > 0:
            joinOperator = " or " if playlistMatch == "one" else " and "
            return "(%s)" % joinOperator.join(sqlWhereClauses)
        else:
            return "(1=1)"

    def __get_rule_sql_where_clause (self, field, operator, value):
        column = self.__get_field_sql_column(field)
        if column:
            if operator == "contains":
                return "%s like '%%%s%%'" % (column, value)
            else:
                return None
        else:
            return None
    
    def __get_field_sql_column (self, field):
        if field == 'path':
            return "pa.strpath"
        else:
            return None
    