select mo.idmovie as id, pa.strpath as path, fi.strfilename as file, nvl(se.strset, '') as settitle, mo.c00 as title, nvl(art.url, '') as poster, nvl(arf.url, '') as fanart
from movie mo
inner join files fi on fi.idfile=mo.idfile
inner join path pa on pa.idpath=fi.idpath
left outer join sets se on se.idset=mo.idset
left outer join art art on art.media_id=mo.idmovie and art.media_type='movie' and art.type='poster'
left outer join art arf on arf.media_id=mo.idmovie and arf.media_type='movie' and arf.type='fanart'
where #PLAYLIST_FILTER#
and nvl(fi.playcount,0) #UNWATCHED_FILTER#
order by RAND()
limit #ITEM_NUMBER#