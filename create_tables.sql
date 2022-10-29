drop table if exists "public".imdb_title_basics_staging;
drop table if exists "public".imdb_title_ratings_staging;

drop table if exists "public".imdb_media;

drop table if exists "public".imdb_runtime;
drop table if exists "public".imdb_genres;
drop table if exists "public".imdb_rating;
drop table if exists "public".imdb_year;


-------------STAGING TABLES
CREATE TABLE "public"."imdb_title_basics_staging"(title_id        character varying(20) encode lzo,
                                                  title_type      character varying(50) encode lzo,
                                                  primary_title   character varying(255) encode lzo,
                                                  originaltitle   character varying(255) encode lzo,
                                                  isadult         character varying(1) encode lzo,
                                                  start_year      numeric(4,0) encode az64,
                                                  end_year        numeric(4,0) encode az64,
                                                  runtime_minutes character varying(255) encode lzo,
                                                  genres          character varying(255) encode lzo);


CREATE TABLE "public"."imdb_title_ratings_staging"(title_id character varying(20) encode lzo,
                                                   rating   numeric(3,1) encode az64,
                                                   numvotes numeric(9,0) encode az64);

-------------FACT TABLE
CREATE TABLE "public"."imdb_media"(id         integer identity(1,1) NOT NULL encode az64,
                                   staging_id character varying(20) encode lzo,
                                   type       character varying(255) encode lzo,
                                   title      character varying(255) encode lzo,
                                   runtime    numeric(5,0) encode az64,
                                   genres     character varying(255) encode lzo,
                                   year       numeric(4,0) encode az64,
                                   rating     numeric(3,1) encode az64,
                                   numvotes   numeric(12,0) encode az64,
                                   CONSTRAINT imdb_media_pkey PRIMARY KEY(id)) distkey(id);

-------------DIMENSON TABLES
CREATE TABLE "public"."imdb_genres"(genres          character varying(255) NOT NULL encode lzo,
                                    has_action      boolean,
                                    has_drama       boolean,
                                    has_crime       boolean,
                                    has_thriller    boolean,
                                    has_romance     boolean,
                                    has_comedy      boolean,
                                    has_sci_fi      boolean,
                                    has_horror      boolean,
                                    has_documentary boolean,
                                    has_animation   boolean,
                                    has_fantasy     boolean,
                                    CONSTRAINT imdb_genres_pkey PRIMARY KEY(genres)) distkey(genres);


CREATE TABLE "public"."imdb_rating"(rating     numeric(3,1) NOT NULL encode az64,
                                    percentile numeric(3,0) encode az64,
                                    CONSTRAINT imdb_rating_pkey PRIMARY KEY(rating)) distkey(rating);

CREATE TABLE "public"."imdb_runtime"(runtime               numeric(5,0) NOT NULL encode az64,
                                     mins_0_to_30          boolean,
                                     mins_31_to_60         boolean,
                                     mins_61_to_90         boolean,
                                     mins_91_to_120        boolean,
                                     mins_121_to_150       boolean,
                                     mins_151_to_180       boolean,
                                     mins_181_to_210       boolean,
                                     mins_greater_than_211 boolean,
                                     CONSTRAINT imdb_runtime_pkey PRIMARY KEY(runtime)) distkey(runtime);

CREATE TABLE "public"."imdb_year"(year   numeric(4,0) NOT NULL encode az64,
                                  decade numeric(4,0) encode az64,
                                  CONSTRAINT imdb_year_pkey PRIMARY KEY(year)) distkey(year);