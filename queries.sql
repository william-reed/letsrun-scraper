use letsrun;
select id from posts order by id desc limit 1;
describe posts;

# most active user (by post count)
select count(author), author from abbreviated where year(datestamp) = 2018 group by author order by count(author) desc limit 5;

# Time Data
# most popular posting dates
select count(datestamp), date(datestamp) from posts group by date(datestamp) order by count(datestamp) desc;
# most popular posting days of the month
select count(day(datestamp)), day(datestamp) from posts group by day(datestamp);
#
# posts per year
select year(datestamp) as y, count(year(datestamp)) from posts group by y order by y asc;

select count(*) from posts;

select * from posts where author = 'bazap';

# view for smaller data
CREATE VIEW abbreviated
	AS select id, thread, parent, author, subject, body, datestamp, cat, main_category, sub_category FROM posts;
    
    

select * from posts where id > 12351 limit 100; 

# most popular threads
SELECT thread, count(thread) FROM posts GROUP BY thread ORDER BY count(thread) desc limit 10;