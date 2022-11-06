select mo.idmovie as id, pa.strpath as path, fi.strfilename as file, ifnull(se.strset, '') as settitle, mo.c00 as title, ifnull(art.url, '') as poster, ifnull(arf.url, '') as fanart
from movie mo
inner join files fi on fi.idfile=mo.idfile
inner join path pa on pa.idpath=fi.idpath
left outer join sets se on se.idset=mo.idset
left outer join art art on art.media_id=mo.idmovie and art.media_type='movie' and art.type='poster'
left outer join art arf on arf.media_id=mo.idmovie and arf.media_type='movie' and arf.type='fanart'
where #PLAYLIST_FILTER#
and ifnull(fi.playcount,0) #UNWATCHED_FILTER#
order by fi.dateadded desc
limit #ITEM_NUMBER#