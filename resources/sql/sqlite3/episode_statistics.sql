select
  (
	select count(0) 
	from episode ep
	inner join files fi on fi.idfile=ep.idfile
	inner join path pa on pa.idpath=fi.idpath
	inner join tvshow tv on tv.idshow=ep.idshow
	where #PLAYLIST_FILTER#) as total,
  (
	select count(0) 
	from episode ep
	inner join files fi on fi.idfile=ep.idfile
	inner join path pa on pa.idpath=fi.idpath
	inner join tvshow tv on tv.idshow=ep.idshow
	where #PLAYLIST_FILTER#
	and ifnull(fi.playcount, 0) > 0) as watched,
  (
	select count(0) 
	from episode ep
	inner join files fi on fi.idfile=ep.idfile
	inner join path pa on pa.idpath=fi.idpath
	inner join tvshow tv on tv.idshow=ep.idshow
	where #PLAYLIST_FILTER#
	and ifnull(fi.playcount, 0) = 0) as unwatched,
  (
	select count(0)
	from (
		select tv.idshow 
		from episode ep
		inner join files fi on fi.idfile=ep.idfile
		inner join path pa on pa.idpath=fi.idpath
		inner join tvshow tv on tv.idshow=ep.idshow
		where #PLAYLIST_FILTER#
		group by tv.idshow) tmp) as totaltvshow
from version
