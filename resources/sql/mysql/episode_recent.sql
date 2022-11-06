select ep.idepisode as id, pa.strpath as path, fi.strfilename as file, tv.c00 as tvshowtitle, ep.c12 as season, ep.c13 as episode, ep.c00 as title, nvl(art.url, '') as thumb, nvl(arf.url, '') as fanart
from tvshow tv
inner join episode ep on ep.idshow=tv.idshow
inner join files fi on fi.idfile=ep.idfile
inner join path pa on pa.idpath=fi.idpath
left outer join art art on art.media_id=ep.idepisode and art.media_type='episode' and art.type='thumb'
left outer join art arf on arf.media_id=tv.idshow and arf.media_type='tvshow' and arf.type='fanart'
where #PLAYLIST_FILTER#
and ep.c12 #SPECIAL_FILTER#
and nvl(fi.playcount,0) #UNWATCHED_FILTER#
order by fi.dateadded desc
limit #ITEM_NUMBER#