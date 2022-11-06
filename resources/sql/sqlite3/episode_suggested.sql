select ep.idepisode as id, pa.strpath as path, fi.strfilename as file, tv.c00 as tvshowtitle, ep.c12 as season, ep.c13 as episode, ep.c00 as title, ifnull(art.url, '') as thumb, ifnull(arf.url, '') as fanart
from tvshow tv
inner join (
	select tv.idshow, min(case when ep.c12=0 then 9999 else cast(ep.c12 as int) end) as c12
	from episode ep
	inner join files fi on fi.idfile=ep.idfile
	inner join path pa on pa.idpath=fi.idpath
	inner join tvshow tv on tv.idshow=ep.idshow
	where #PLAYLIST_FILTER#
	and ep.c12 #SPECIAL_FILTER#
	and ifnull(fi.playcount,0)=0
	group by tv.idshow
) nextseason on nextseason.idshow=tv.idshow
inner join (
	select tv.idshow, (case when ep.c12=0 then 9999 else cast(ep.c12 as int) end) as c12, min(cast(ep.c13 as int)) as c13
	from episode ep
	inner join files fi on fi.idfile=ep.idfile
	inner join path pa on pa.idpath=fi.idpath
	inner join tvshow tv on tv.idshow=ep.idshow
	where #PLAYLIST_FILTER#
	and ep.c12 #SPECIAL_FILTER#
	and ifnull(fi.playcount,0)=0
	group by tv.idshow, ep.c12
) nextepisode on nextepisode.idshow=tv.idshow and nextepisode.c12=nextseason.c12
inner join episode ep on ep.idshow=tv.idshow and ep.c12=(case when nextseason.c12=9999 then 0 else nextseason.c12 end) and ep.c13=nextepisode.c13
inner join files fi on fi.idfile=ep.idfile
inner join path pa on pa.idpath=fi.idpath
left outer join art art on art.media_id=ep.idepisode and art.media_type='episode' and art.type='thumb'
left outer join art arf on arf.media_id=tv.idshow and arf.media_type='tvshow' and arf.type='fanart'
inner join (
	/* Serie avec des episodes vus */
	select tv.idshow, 1 as priority, (case when notplayedmindateadded.dateadded>maxlastplayed.lastplayed then notplayedmindateadded.dateadded else maxlastplayed.lastplayed end) as updatetime
	from tvshow tv
	inner join (
		select tv.idshow, min(fi.dateadded) as dateadded
		from episode ep
		inner join files fi on fi.idfile=ep.idfile
		inner join path pa on pa.idpath=fi.idpath
		inner join tvshow tv on tv.idshow=ep.idshow
		where #PLAYLIST_FILTER#
		and ep.c12 #SPECIAL_FILTER#
		and ifnull(fi.playcount,0)=0
		group by tv.idshow
	) notplayedmindateadded on notplayedmindateadded.idshow = tv.idshow
	inner join (
		select tv.idshow, max(fi.lastplayed) as lastplayed
		from episode ep
		inner join files fi on fi.idfile=ep.idfile
		inner join path pa on pa.idpath=fi.idpath
		inner join tvshow tv on tv.idshow=ep.idshow
		where #PLAYLIST_FILTER#
		and ep.c12 #SPECIAL_FILTER#
		group by tv.idshow
	) maxlastplayed on maxlastplayed.idshow = tv.idshow
	where tv.idshow in (
		select tv.idshow
		from episode ep
		inner join files fi on fi.idfile=ep.idfile
		inner join path pa on pa.idpath=fi.idpath
		inner join tvshow tv on tv.idshow=ep.idshow
		where #PLAYLIST_FILTER#
		and ep.c12 #SPECIAL_FILTER#
		and ifnull(fi.playcount,0)>0)
	union
	/* Serie sans episode vu */
	select tv.idshow, 2 as priority, maxdateadded.dateadded as updatetime
	from tvshow tv
	inner join (
		select tv.idshow, max(fi.dateadded) as dateadded
		from episode ep
		inner join files fi on fi.idfile=ep.idfile
		inner join path pa on pa.idpath=fi.idpath
		inner join tvshow tv on tv.idshow=ep.idshow
		where #PLAYLIST_FILTER#
		and ep.c12 #SPECIAL_FILTER#
		group by tv.idshow
	) maxdateadded on maxdateadded.idshow = tv.idshow
	where tv.idshow not in (
		select tv.idshow
		from episode ep
		inner join files fi on fi.idfile=ep.idfile
		inner join path pa on pa.idpath=fi.idpath
		inner join tvshow tv on tv.idshow=ep.idshow
		where #PLAYLIST_FILTER#
		and ep.c12 #SPECIAL_FILTER#
		and ifnull(fi.playcount,0)>0)
) tvshowstat on tvshowstat.idshow=tv.idshow
order by tvshowstat.priority, tvshowstat.updatetime desc
limit #ITEM_NUMBER#