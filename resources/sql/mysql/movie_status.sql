select mo.idmovie as id, fi.dateadded, fi.lastplayed, nvl(fi.playcount,0) as playcount, cast(nvl(bo.timeinseconds,0) as INT) as resumetime, mo.c11 as totaltime
from movie mo
inner join files fi on fi.idfile=mo.idfile
inner join path pa on pa.idpath=fi.idpath
left outer join bookmark bo on bo.idfile=fi.idfile and bo.type=1
where mo.idmovie=#ID#