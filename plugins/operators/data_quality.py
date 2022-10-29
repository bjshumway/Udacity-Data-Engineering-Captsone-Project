from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="redshift",
                 aws_credentials_id = "aws_credentials",
                 region = 'us-west-2',
                 checks = [],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.checks = checks
        self.region = region
        
    def execute(self, context):
        self.log.info('Executing inside data_quality')
        
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift_hook = PostgresHook("redshift")
        
                
        for check in self.checks:
            query = check['query']
            rslt = check['rslt']
            rows = redshift_hook.get_records(query)[0]
            if rows[0] == rslt:
                self.log.info("Query: {} --- SUCCESS!".format(query))
            else:
                raise ValueError("Error! Query {}, failed with {}".format(query,rows[0]))
                
            