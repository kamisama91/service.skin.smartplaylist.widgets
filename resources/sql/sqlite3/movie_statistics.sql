select
  (
	select count(0) 
	from movie mo
	inner join files fi on fi.idfile=mo.idfile
	inner join path pa on pa.idpath=fi.idpath
	left outer join sets se on se.idset=mo.idset
	where #PLAYLIST_FILTER#) as total,
  (
	select count(0)
	from movie mo
	inner join files fi on fi.idfile=mo.idfile
	inner join path pa on pa.idpath=fi.idpath
	left outer join sets se on se.idset=mo.idset
	where #PLAYLIST_FILTER#
	and ifnull(fi.playcount, 0) > 0) as watched,
   (
	select count(0)
	from movie mo
	inner join files fi on fi.idfile=mo.idfile
	inner join path pa on pa.idpath=fi.idpath
	left outer join sets se on se.idset=mo.idset
	where #PLAYLIST_FILTER#
	and ifnull(fi.playcount, 0) = 0) as unwatched,
  (
	select count(0)
	from (
		select mo.idset
		from movie mo
		inner join files fi on fi.idfile=mo.idfile
		inner join path pa on pa.idpath=fi.idpath
		inner join sets se on se.idset=mo.idset
		where #PLAYLIST_FILTER#
		group by mo.idset) tmp) as totalset
from version
