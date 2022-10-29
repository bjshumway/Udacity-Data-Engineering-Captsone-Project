from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook


class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 sql,
                 table,
                 redshift_conn_id="redshift",
                 aws_credentials_id = "aws_credentials",
                 region = 'us-west-2',
                 jsonpath= 'auto',
                 append_or_truncate='truncate',                 
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.region = region
        self.jsonpath = jsonpath
        self.sql = sql
        self.table = table
        self.append_or_truncate = append_or_truncate

    def execute(self, context):
        self.log.info('Executing inside load_fact')
        
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