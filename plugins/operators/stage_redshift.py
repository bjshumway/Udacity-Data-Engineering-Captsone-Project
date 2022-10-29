from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook


class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'


    @apply_defaults
    def __init__(self,
                 redshift_conn_id="redshift",
                 aws_credentials_id = "aws_credentials",
                 table = "",
                 s3_path="s3://imdbdataforudacityproject",
                 s3_bucket="",
                 s3_key="",
                 region = 'us-west-2',
                 jsonpath= 'auto',
                 max_errors = 0,
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)

        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_path = s3_path
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.region = region
        self.jsonpath = jsonpath
        self.max_errors = max_errors
        
        
        
        
    def execute(self, context):
        self.log.info('Executing inside stage_redshift')
        
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id = self.redshift_conn_id)

        self.log.info('Copying data from S5 to Redshift')
           
        redshift.run(
        """
        DELETE FROM {}
        """.format(self.table)
        )

        #Consume the Tab Separated File        
        #Source: https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-format.html#copy-format
        #We set Max Errors to 70,000 because that only represents losing 1% of the data
        #This is fine for our purposes
        redshift.run(
        """
        COPY {}
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        REGION '{}'
        DELIMITER '\t'
        IGNOREHEADER 1
        MAXERROR {}
        """.format(
            self.table,
            self.s3_path + '/' + self.s3_bucket + '/' + self.s3_key,
            credentials.access_key,
            credentials.secret_key,
            self.region,
            self.max_errors))





