from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

default_args = {
    'owner': 'IMDB_ANALYSIS',
    'start_date': datetime(2022, 10, 2),
    'depends_on_past': False,
    #'retries': 3, 
    #'retry_delay': timedelta(minutes=5),
    'catchup' : False
}

dag = DAG('imdb_analysis13',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval= '@once',
          max_active_runs= 1
         )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_titles_to_redshift = StageToRedshiftOperator(
    task_id='stage_title_basics',
    table = 'imdb_title_basics_staging',
    s3_bucket = 'imdbdataforudacityproject',
    s3_key='title.basics.tsv',
    s3_path='s3:/',
    max_errors=70000, #70,000 might seem like a big number but there are 700,000 rows. So its only 1%
    dag=dag
)

stage_title_ratings_to_redshift = StageToRedshiftOperator(
    task_id='stage_title_ratings',
    table = 'imdb_title_ratings_staging',
    s3_bucket = 'imdbdataforudacityproject',
    s3_key='title.ratings.tsv',
    s3_path='s3:/',
    max_errors=10000, #10,000 might seem like a big number but there are 1 million rows. So its only 1%
    dag=dag
)

load_media_table = LoadFactOperator(
    task_id='load_media_table',
    dag=dag,
    sql=SqlQueries.media_insert,
    table='imdb_media',
    append_or_truncate='truncate'
)

load_genres_dimension_table = LoadDimensionOperator(
    task_id='Load_genres_dim_table',
    table='imdb_genres',
    append_or_truncate='truncate',
    dag=dag,
    sql=SqlQueries.genres_insert
)

load_rating_dimension_table = LoadDimensionOperator(
    task_id='Load_rating_dim_table',
    table='imdb_rating',
    append_or_truncate='truncate',
    dag=dag,
    sql=SqlQueries.rating_insert
)

load_runtime_dimension_table = LoadDimensionOperator(
    task_id='Load_runtime_dim_table',
    table='imdb_runtime',
    append_or_truncate='truncate',
    dag=dag,
    sql=SqlQueries.runtime_insert
)


load_year_dimension_table = LoadDimensionOperator(
    task_id='Load_year_dim_table',
    table='imdb_year',
    append_or_truncate='truncate',
    dag=dag,
    sql=SqlQueries.year_insert
)


run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    checks=[{'query':'select count(*) from imdb_media where title is null',
             'rslt': 0},
            {'query':'select count(*) from imdb_rating where rating = 9',
             'rslt': 1},
           ],
    dag=dag
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> stage_titles_to_redshift
start_operator >> stage_title_ratings_to_redshift

stage_title_ratings_to_redshift >> load_media_table
stage_titles_to_redshift >> load_media_table

load_media_table >> load_genres_dimension_table
load_media_table >> load_rating_dimension_table
load_media_table >> load_runtime_dimension_table
load_media_table >> load_year_dimension_table


load_genres_dimension_table >> run_quality_checks
load_rating_dimension_table >> run_quality_checks
load_runtime_dimension_table >> run_quality_checks
load_year_dimension_table >> run_quality_checks

run_quality_checks >> end_operator


