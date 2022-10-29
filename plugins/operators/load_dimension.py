from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook


class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 table,
                 sql,
                 redshift_conn_id="redshift",
                 aws_credentials_id = "aws_credentials",
                 region = 'us-west-2',
                 jsonpath= 'auto',
                 append_or_truncate = 'append',
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.region = region
        self.jsonpath = jsonpath
        self.append_or_truncate = append_or_truncate
        self.sql = sql

    def execute(self, context):
        self.log.info('Loading Table: ' + self.table)

        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id = self.redshift_conn_id)
        
        if(self.append_or_truncate == 'truncate'):
            redshift.run(
               """
               DELETE FROM {}
               """.format(self.table)
            )
        
        
        insert_sql = '''
                     INSERT INTO public.{destination_table}
                     {sql}
                     '''.format(destination_table=self.table,sql=self.sql)

        redshift.run(
          insert_sql
        )
        
        

