select ep.idepisode as id, fi.dateadded, fi.lastplayed, nvl(fi.playcount,0) as playcount, cast(nvl(bo.timeinseconds,0) as INT) as resumetime, ep.c09 as totaltime
from episode ep
inner join files fi on fi.idfile=ep.idfile
inner join path pa on pa.idpath=fi.idpath
left outer join bookmark bo on bo.idfile=fi.idfile and bo.type=1
where ep.idepisode=#ID#