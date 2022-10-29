# IMBD DATA WAREHOUSING W/ AMAZON REDSHIFT & APACHE AIRFLOW
*Capstone Project*

## *Important* (please read)
To use Apache Airflow I utilized the workspace for the project "Data Pipelines". Please go to that project and look at the files "final_project_dag.py", "create_tables.sql", and "sql_queries.py". If you intend to try running my code to prove to yourself that it works... please run "create_tables.sql" in your Amazon Redshift... then you can go ahead and run ./opt/airflow/start.sh. 

To view the "Data Dictionary" see the image "Data Dictionary.png". 

## Project Goal
The goal of this project is to create an ETL Pipeline to pull data from IMDB (The preiminent movie database online), and put it into a standard data warehousing data model... so that statistics / graphs can be run on it for business insight.

## What queires would be run based on this model?
Many different queires can be run against the data model I have created. It include things such as "What movies are in the 99th percentile" (as far as rating), "What genres are the most common?", "How does runtime affect a movie's average rating", "How has the popularity of different movie genres changed from decade to decade?".

Each of these questions are now answered! Checkout the file "Four Queries to Gain Business Insight on The Movie Industry.docx" as proof that I ran the queries, and that the data is properly populated.

## How is Airflow Incorporated
The advantages of using airflow in this project are many. Airflow allows you to create a direct-graph set of tasks, and run them in the appropriate order, with "dependent" tasks waiting until their "parent" task finishes first. By explicitly breaking your code into tasks, your code becomes more modular. You can define operators for example that you can think of as a "type of task"... so you can run many tasks of that type with slightly different parameters. Airflow also allows you to run tasks in parralel, which can help speed up the ETL pipeline. Airflow gives you a "birds eye view" of your ETL pipeline because you can see your move through their various states. Airflow also offers the ability to back-fill tasks, so your code can run for events that occurred in the past, e.g. if you have to backfill tax records... Airflow can run your code for 2020/2021/2022 simultaniously.

Airflow and Amazon Redshift are a natural fit. Database developers who use tools like Redshift often don't realize that techniques such as Airflow are so powerful. This is because they are in the "bad habit" of running their code "top-to-bottom" from "installation files".... which breads messiness and confusion. Enter Apache Airflow which, for the reasons mentioned in the previous paragraph, solves this issue.

## Model Choices

To view the "Data Dictionary" see the image "Data Dictionary.png". 

The model I chose to create is a standard star schema. I created the fact table "IMDB_MEDIA", and the four dimensional tables "imdb_genres", "imdb_rating", "imdb_runtime", and "imdb_year". At first I thought this might not be enough as these tables are only populated from two IMDB files found at [here](https://www.imdb.com/interfaces)... namely title.basics.tsv.gz and title.ratings.tsv.gz.... my original goal was to also include the file name.basics.tsv.gz.

### First Data Source: title.basics.tsv.gz
This file contains 1 million rows of the different kinds of media that IMDB tracks... I use the term "media" to represent movies, t.v. shows, video games, etc.. The file contains the title, genre, start year / end year, runtime (in minutes), etc.

### Second Data Source: title.rating.tsv.gz
This file has a 1 to 0 relationship with title.basics.... basically any peace of media either has been rated (by 1 or more people) or it hasn't ever gotten a rating. The file contains the rating, and the number or votes, for each media that has been rated

### Third Data Source: name.basic.tsv.gz (Not used... but I did explore it)
This contains the names of actors / actresses / producers / directors, etc. as well as their information such as year of birth, year of death (assuming they passed away), and what media (i.e.e movies/t.v. shows etc.) they are best known for. This is the biggest file by far with over 10 million rows! I was originally very enticed in adding the data from name.basic.tsv.gz into my data model. I wanted to include a "cool" dimension table called "imdb_average_actor_rating", so that you can compare different films by their actor's rating, and see the relationship between the actor's ratings and the film's rating. However... since the actors don't have a rating in the name.basic.tsv.gz file... I would have to write a query that would average their rating across all movies they are known for.... and then for each media on my fact table... average the rating of the actors in that fact table. That last step is pretty hard because with 1 million rows of media... and 10 million rows of names... you're looking at gargantuan amounts of looping in the join clause of the query. Okay... maybe we can scale back and try to be less cool! I learned here that "less is more"... if you look at the section "What queires would be run based on this model"... you can see that even from two IMDB files, you can gain a lot of insight on the movie industry!

So now lets return to "Model Choices", and consider how I setup my dimension tables.

### imdb_genres
This is uniquely defined by its "genres" column which is a "comma separated list" that's connect by foreign-key to the fact table. So if in my fact table the "genres" column is "Action,Thriller,Romance"... there will be a row in imdb_genres with the genres column "Action,Thriller,Romance". But thinking carefully the business analys may care about slicing the fact table into just "Action" or just "Thriller", and for that I solved the problem by creating the columns has_action, has_thriller, and has_romance.

### imdb_rating
This is uniquely defined by its "rating" column which is a number from 1 to 10. I imagined that the business analyst would care more about the "percentile" of the rating than the actual rating itself. For example, if a movie has a rating of 6... what percentile does that place it in? The 35 percentile! That means that roughly 2/3rd of all movies have a better rating than it! Meanwhile if a movie has a rating of 9 what percentile is it in? The 97th percentile. That's right... to have a 9 for a rating means you are rated in the top 3% of movies!

### imdb_runtime
This is uniquely defined by the runtime column... which is measured in minutes. I anticipate that the bar-charts you can plot against runtime will be too busy-looking since the it's hard to fit 120 bars on the same screen, if you're looking at movies with times ranging from 1 minute to 120 minutes. So I created columns "mins_0_to_30", "mins_31_to_60", "mins_61_to_90", etc. so that the dimension table can be used to chart movies by time "more generally".

### imdb_year
The last dimension table is imdb_year... which contains a column "decade", so that you can chart movies by decade, instead of just by year, if you're trying to tease out overall trends in the movie industry as the decades have gone by.


## What is the rationale for the choice of tools and technologies for the project?
I think the earlier paragraph "How is Airflow Incorporated" largely answers this question. However I should point out the advantages of amazon redshift. First, since its in the cloud, you don't have to deal with the difficult decisions of building a custom database. You don't have to, for example, "buy more ram", or "deal with power outages" etc. Now where Amazon Redshift really shines is that it's built primarilly for data-warehousing. For example, it uses columnar format (instead of row formatting) which while making complex queires rather slow.... since data-warehousing queires are pretty straightforward (let's face it... a star schema lends itself to simple queires) the query time is much faster. Queries where you need to lookup subsets of your data... for example, a sum on a "salary" column, become much faster with columnar formatting because all of the data is gathered right away from the single column... you don't have to go hunting through row-after-row of data... meaning less hard-drive disk-seeks. Redshift also uses distkeys to split your query so that it can be run on multiple processors simultaniously.

## The steps of the process.
To run the code you will need an environment setup for Amazon Redshift and Apache Airflow. You will want to enter two 'connections' into Aifrlow... namely one for Redshift (i.e. the host, the port, the connection type of "PostGres", etc.)... and the one for AWS (the usernam/password, namely the AWS Access Key and the AWS Secret Key). I used the environment already setup for me by Udacity in their project "Data Pipelines"... so dear reader if you are grading this project, please check there to see my code in that project... you can run it there. Once the environment is setup, you can run "/opt/airflow/start.sh" to start the airflow server. Then navigate to the server URL, and you will see the DAG called "imdb_analysis13". The DAG should start running by default... but if it doesn't then make sure the DAG is turned "On". If it still doesn't start running right away, then you can click the 'run' button to run the DAG.


Once the DAG starts running here are the steps it takes:

### Task 1: Start Operator
This simply notes that the DAG started running

### Task 2 & 3: (Run simultaniously) stage_titles_to_redshift  & stage_title_ratings_to_redshift 
These run the "COPY" command to copy the two files from S3 to Redshift

### Task 4: load_media_table 
This builds the fact table "media" by querying the two staging tables

### Task 5,6,7,8: (Run simultaniously) load_genres_dimension_table load_rating_dimension_table, load_runtime_dimension_table, load_year_dimension_table 
This builds the dimension tables

### Task 9: run_quality_checks 
This runs two data quality checks (discussed below)

### Task 10: End Operator
This simply notes that the DAG finished running


### Here is a full synopsis of how the ETL pipeline flows start to finish:
First, we use Amazon S3 to store the two files "title.basics.tsv" and "title.rating.tsv"... in the real world we would probably use a database connection the IMDB's servers (after negotiating a business deal with them)... but for now this is a fine "stand-in" for "proof-of-concept". Now the fun begins. We setup Apache Airflow to run on a schedule... so that it pulls this data from S3 and writes it to staging tables in Redshift. From here we create the fact table. After that we create the dimension tables. Finally we perform our data quality checks to make sure the data is itself valid. Since this is a "proof-of-concept" I only include TWO data checks. These are
1. The fact table (imdb_media) doesn't have any Null titles... 
2. The dimension table imdb_rating has a row where the rating is '9'.

## Propose how often the data should be updated and why.
If this project were to no longer be "proof of concept", I would imagine the data should be run on a monthly basis. This is because the statistics it gathers are so vast, that I don't foresee big changes in the data on a day-to-day or even weekly basis. This is also because the scope of the project would increase (e.g. including the "names" file like I mentioned above) since IMDB actually has over a dozen of these files, and they are all a goldmine. You can save money by running the ETL process on a monthly basis rather than a weekly basis, especially if the ETL process takes hours to run (as I expect it would). However... if we are a "lean" startup company and truly only care about data from the two files (name.basic and ratings.basic)... well... maybe we would want to run Apache Airflow on a weekly basis... since it only takes a few minutes to run... and who knows... maybe we are looking for quick short-lived trends, rather than large overall trends.

## Post your write-up and final data model in a GitHub repo.
Done. The github is located at: https://github.com/bjshumway/Udacity-Data-Engineering-Captsone-Project


## Include a description of how you would approach the problem differently under the following scenarios:
### If the data was increased by 100x.
At 100 times more data, this project would require more compute. While the entire DAG takes about 100 minutes to run... a 100x increase in the data will lead to an exponentially slower compute-time... as the query for the fact table requires a join. Joins slow down exponentially because for each row in the parent table (which lets say is now 100 times bigger) you have to loop through each row in the child table. Since Amazon Redshift is performant-slow when it uses joins (due to it being a columnar database).... we could consider using a standard database, such as Amazon EC3, to build the fact table.... but then write that fact table (afters its been built) directly to Amazon Redshift. Another approach would be to use distributed computing techniques, like spark, which would allow us to spin up multiple machines to distribute the query across all of them. Lastly, with Amazon you can purchase different database sizes to meet your needs. A database that is optimized for CPU for example may prove useful. Amazon EC2 for example can support up to 48 cores! You just gotta be willing to pay the money.
    
    
### If the pipelines were run on a daily basis by 7am.
Running the pipelines on a daily basis (7am) with the current project wouldn't be an issue at all! The reason is because the project only takes one minute to run. However... if we imagine that this project increases in scope (as all projects do once they go from proof-of-concept to professional-grade)... then the data may take "too long" before its ready to be consumed. For example if you have 9am meeting, and you need to look at the data from today.... but the data takes 3 hours to run... well you're going to have to postpone the meeting. This is why I think 7am is not a good time to run these jobs. In fact most companies run their data-warehousing jobs ealier, like at 12am or 1am.
    
### If the database needed to be accessed by 100+ people.
If this project needed to access by 100+ people, we are looking at a lot of reads... and would have to consider a tool such as Apache Cassandra. Since Cassandra is a very focused tool (think of it like a giant dictionary), we would need to truly understand our user's business needs. Perhaps they care about only one or two metrics... such as the number of votes a given film has... we can use Apache Cassandra to store as a dictionary the film's title (as the key) and the number of votes (as the value). This is how for example twitter handles millions of people looking at the number of upvotes for a given tweat. However Cassandra isn't great at handling the more "generalized" needs of a data warehouse... and if 100+ people truly need to access this star-schema... which was built for statistics and charts... then we could use a tool like spark to distribute their queries across multiple computers. Spark has another advantage in that it optimizes for keeping the data in ram (instead of disk)... which will speed up people's queires, especially if there is a pattern in the kinds of queries they like to perform. 
    
    
    
    