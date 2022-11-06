select mo.idmovie as id, pa.strpath as path, fi.strfilename as file, nvl(se.strset, '') as settitle, mo.c00 as title, nvl(art.url, '') as poster, nvl(arf.url, '') as fanart, fi.*
from movie mo
inner join (
	/*films en cours de lecture*/
	select mo.idmovie, 1 as priority, fi.lastplayed as updatetime
	from movie mo
	inner join files fi on fi.idfile=mo.idfile
	inner join path pa on pa.idpath=fi.idpath
	left outer join sets se on se.idset=mo.idset
	where #PLAYLIST_FILTER#
	and nvl(fi.playcount,0) = 0
	and fi.lastplayed is not null
	union
	/*1er film sorti et non vu pour les sets avec des films vus et sans film en cours de lecture*/
	select mo.idmovie, 2 as priority, setstarted.updatetime
	from sets se
	inner join (
		select se.idset, mo.idmovie
		from sets se
		inner join (
			select se.idset, min(mo.premiered) as premiered
			from sets se
			inner join movie mo on mo.idset=se.idset
			inner join files fi on fi.idfile=mo.idfile
			inner join path pa on pa.idpath=fi.idpath
			where #PLAYLIST_FILTER#
			and nvl(fi.playcount,0) = 0
			group by se.idset
		) setnextpremiered on setnextpremiered.idset=se.idset
		inner join movie mo on mo.idset=setnextpremiered.idset and mo.premiered=setnextpremiered.premiered
	) nextmovie on nextmovie.idset=se.idset
	inner join movie mo on mo.idmovie=nextmovie.idmovie
	inner join (
		select se.idset, if(notplayedmindateadded.dateadded>maxlastplayed.lastplayed,notplayedmindateadded.dateadded,maxlastplayed.lastplayed) as updatetime
		from sets se
		inner join (
			select se.idset, min(fi.dateadded) as dateadded
			from sets se
			inner join movie mo on mo.idset=se.idset
			inner join files fi on fi.idfile=mo.idfile
			inner join path pa on pa.idpath=fi.idpath
			where #PLAYLIST_FILTER#
			and nvl(fi.playcount,0) = 0
			group by se.idset
		) notplayedmindateadded on notplayedmindateadded.idset = se.idset
		inner join (
			select se.idset, max(fi.lastplayed) as lastplayed
			from sets se
			inner join movie mo on mo.idset=se.idset
			inner join files fi on fi.idfile=mo.idfile
			inner join path pa on pa.idpath=fi.idpath
			where #PLAYLIST_FILTER#
			group by se.idset
		) maxlastplayed on maxlastplayed.idset = se.idset
		where se.idset in (
			select se.idset
			from sets se
			inner join movie mo on mo.idset=se.idset
			inner join files fi on fi.idfile=mo.idfile
			inner join path pa on pa.idpath=fi.idpath
			where #PLAYLIST_FILTER#
			and nvl(fi.playcount,0) > 0)
	) setstarted on setstarted.idset=se.idset
	where se.idset not in (
		select se.idset
		from sets se
		inner join movie mo on mo.idset=se.idset
		inner join files fi on fi.idfile=mo.idfile
		inner join path pa on pa.idpath=fi.idpath
		where #PLAYLIST_FILTER#
		and nvl(fi.playcount,0) = 0
		and fi.lastplayed is not null)
       union    
       /*film non vu / non en cours*/
	select mo.idmovie, 3 as priority, fi.dateadded as updatetime
	from movie mo
	inner join files fi on fi.idfile=mo.idfile
	inner join path pa on pa.idpath=fi.idpath
	left outer join sets se on se.idset=mo.idset
	where #PLAYLIST_FILTER#
	and nvl(fi.playcount,0) = 0
	and fi.lastplayed is null
	and mo.idset is null
	union
	/*1er film sorti pour les sets non vu / non en cours => meme protité que les films non vu*/
	select mo.idmovie, 3, maxdateadded.dateadded as updatetime
	from sets se
	inner join (
		select se.idset, mo.idmovie
		from sets se
		inner join (
			select se.idset, min(mo.premiered) as premiered
			from sets se
			inner join movie mo on mo.idset=se.idset
			inner join files fi on fi.idfile=mo.idfile
			inner join path pa on pa.idpath=fi.idpath
			where #PLAYLIST_FILTER#
			and nvl(fi.playcount,0) = 0
			group by se.idset
		) setnextpremiered on setnextpremiered.idset=se.idset
		inner join movie mo on mo.idset=setnextpremiered.idset and mo.premiered=setnextpremiered.premiered
	) nextmovie on nextmovie.idset=se.idset
	inner join movie mo on mo.idmovie=nextmovie.idmovie
	inner join (
		select se.idset, max(fi.dateadded) as dateadded
		from sets se
		inner join movie mo on mo.idset=se.idset
		inner join files fi on fi.idfile=mo.idfile
		inner join path pa on pa.idpath=fi.idpath
		where #PLAYLIST_FILTER#
		group by se.idset
	) maxdateadded on maxdateadded.idset = se.idset
	where se.idset not in (
		select se.idset
		from sets se
		inner join movie mo on mo.idset=se.idset
		inner join files fi on fi.idfile=mo.idfile
		inner join path pa on pa.idpath=fi.idpath
		where #PLAYLIST_FILTER#
		and ((nvl(fi.playcount,0) = 0 and fi.lastplayed is not null) 
		     or (nvl(fi.playcount,0) > 0)))
) moviestat on moviestat.idmovie = mo.idmovie
inner join files fi on fi.idfile=mo.idfile
inner join path pa on pa.idpath=fi.idpath
left outer join sets se on se.idset=mo.idset
left outer join art art on art.media_id=mo.idmovie and art.media_type='movie' and art.type='poster'
left outer join art arf on arf.media_id=mo.idmovie and arf.media_type='movie' and arf.type='fanart'
order by moviestat.priority, moviestat.updatetime desc
limit #ITEM_NUMBER#