from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id='sales_etl_pipeline',
    start_date=datetime(2025, 10, 20),
    schedule='@daily', # <--- CHANGE THIS LINE
    catchup=False,
    description='A simple ETL pipeline for the Superstore sales data.'
) as dag:

    # Define the task
    run_etl_script = BashOperator(
        task_id='run_etl_script',
        bash_command='cd /home/khan/etl_project && source venv/bin/activate && python etl_to_postgres.py'
    )

    # Set the task dependencies (we only have one task)
    run_etl_script