
insert batchmission 
values ("nano+align+stage", "main");

insert batchmission 
values ("nano+align+stage", "detail");

insert batchmission 
values ("chip+to+wafer", "main");

insert batchmission 
values ("chip+to+wafer", "detail");
insert batchmission 
values ("nano+vision+align", "main");

insert batchmission 
values ("nano+vision+aligne", "detail");
insert batchmission 
values ("semiconductor+packaging", "main");

insert batchmission 
values ("semiconductor+packaging", "detail");
insert batchmission 
values ("AI+deep+learning", "main");

insert batchmission 
values ("AI+deep+learning", "detail");


    CREATE TABLE breakage LIKE naver; 
    INSERT breakage SELECT * FROM naver;



insert batchmission 
values ("spontaneous+glass+breakage", "main");

insert batchmission 
values ("spontaneous+glass+breakage", "detail");

delete from batchmission;

delete from naver where subject='cigs+solar+cell';

delete from naver where subject="encapsulation+emulsion";

select * from naver where subject='cigs+solar+cell' order by publish_year;

select distinct category from naver where subject='cigs+solar+cell';
 


SELECT * FROM scholar.batchmission;
select * from naver where subject='encapsulation'; 


SELECT count(*) FROM naver 
where subject='cigs+solar+cell';

SELECT count(*) FROM naver where subject='cigs+solar+cell';
SELECT * FROM naver where subject='cigs+solar+cell';



delete from batchmission where searchsubject='cigs+solar+cell';
delete from batchmission where searchsubject='encapsulation' and mainORdetail='main';


select author, length(author) from scholar.naver where length(author) >100;


CREATE TABLE encapsulation LIKE naver; 
INSERT encapsulation SELECT * FROM naver;

insert batchmission values ("nano+align+stage", "main");

insert batchmission values ("chip+to+wafer", "main");


insert batchmission values ("nano+vision+align", "main");

insert batchmission values ("semiconductor+packaging", "main");


insert batchmission values ("nano+align+stage", "detail");
insert batchmission values ("chip+to+wafer", "detail");
insert batchmission values ("nano+vision+aligne", "detail");
insert batchmission values ("semiconductor+packaging", "detail");


insert batchmission 
values ("AI+deep+learning", "main");

insert batchmission 
values ("AI+deep+learning", "detail");


SELECT * FROM scholar.batchmission;
select title_link from scholar.naver where subject='nano+align+stage' and abstract is null or abstract ='Empty') order by idnaver;
select title_link from scholar.naver where (abstract is null or abstract ='Empty') order by idnaver;
select title_link from scholar.naver where abstract ='Empty' order by idnaver;

select * from naver where subject='AI+deep+learning';
select * from naver where subject='chip+to+wafer';
select * from naver where subject='nano+align+stage';
select * from naver where subject='nano+vision+align';
select * from naver where subject='semiconductor+packaging';