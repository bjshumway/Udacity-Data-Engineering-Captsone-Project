class SqlQueries:
    media_insert = ("""(staging_id,
                       type,
                       title,
                       runtime,
                       year,
                       numvotes,
                       rating,
                       genres)
select t.title_id,
       t.title_type,
       t.primary_title,
       cast(t.runtime_minutes as numeric),
       t.start_year,
       r.numvotes,
       r.rating,
       t.genres
  from imdb_title_basics_staging t
  join imdb_title_ratings_staging r on r.title_id = t.title_id;""")
    genres_insert = ("""(genres,has_action,has_drama,has_crime,has_thriller,has_romance,has_comedy,has_sci_fi,has_horror,has_documentary,has_animation,has_fantasy)
select distinct
       genres,
       strpos(genres,'Action') > 0,
       strpos(genres,'Drama') > 0,
       strpos(genres,'Crime') > 0,
       strpos(genres,'Thriller') > 0,
       strpos(genres,'Romance') > 0,
       strpos(genres,'Comedy') > 0,
       strpos(genres,'Sci-Fi') > 0,
       strpos(genres,'Horror') > 0,
       strpos(genres,'Documentary') > 0,
       strpos(genres,'Animation') > 0,
       strpos(genres,'Fantasy') > 0
  from imdb_title_basics_staging t
 where genres is not null;""")
    rating_insert = ("""(rating,percentile)
select rating,
       max(percentiles) as percentile
       /* Fascinating: "7" is the median rating! */
  from (
select rating,
       ntile(100) over (order by rating) percentiles /*Source: https://leafo.net/guides/postgresql-calculating-percentile.html*/
  from imdb_title_ratings_staging t
 where rating is not null
  )
  group by rating;""")
    runtime_insert = ("""(runtime,mins_0_to_30,mins_31_to_60,mins_61_to_90,mins_91_to_120,mins_121_to_150,mins_151_to_180,mins_181_to_210,mins_greater_than_211)
select distinct
       runtime_minutes,
       runtime_minutes between 0 and 30,
       runtime_minutes between 31 and 60,
       runtime_minutes between 61 and 90,
       runtime_minutes between 91 and 120,
       runtime_minutes between 121 and 150,
       runtime_minutes between 151 and 180,
       runtime_minutes between 181 and 210,
       runtime_minutes > 211
  from imdb_title_basics_staging
 where runtime_minutes is not null;""")
    year_insert = ("""(year,decade)
select distinct
       start_year,
       round(start_year,-1) as decade
  from imdb_title_basics_staging
 where start_year is not null
  order by start_year;""")
