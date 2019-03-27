import json
import time
from base64 import b64encode
from datetime import timedelta

import airflow
from airflow import DAG

from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.operators.bash_operator import BashOperator
from servian.operators import PubSubPublishCallableOperator


def encode_pubsub_data(data):
    return b64encode(json.dumps(data).encode()).decode()


def get_pubsub_messages(**context):
    return [
        {
            "data": encode_pubsub_data(
                {
                    "inserted_ms": int(round(time.time() * 1000)),
                    "dag_run_id": context["dag_run"].run_id,
                    "dag_id": context["dag"].dag_id,
                    "status": "Success",
                }
            )
        }
    ]


# these args will get passed on to each operator
# you can override them on a per-task basis during operator initialization
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": airflow.utils.dates.days_ago(2),
    "schedule_interval": None,
    "email": ["chris.tippett@servian.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "project": "gcp-batch-pattern"
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'adhoc':False,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'trigger_rule': u'all_success'
}

with DAG(
    "bigquery_demo",
    default_args=default_args,
    description="A simple tutorial DAG",
    schedule_interval=timedelta(days=1),
) as dag:

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = BigQueryOperator(
        task_id="truncate-bigquery-table",
        sql="DELETE FROM `gcp-batch-pattern.composer_demo.demo_counter` WHERE 1=1",
        use_legacy_sql=False,
        location="US",
    )

    t2 = BigQueryOperator(
        task_id="insert-into-bigquery-table",
        sql="SELECT MAX(counter) + 1 AS counter from `gcp-batch-pattern.composer_demo.demo_counter`",
        use_legacy_sql=False,
        destination_dataset_table="composer_demo.demo_counter",
        location="US",
        write_disposition="APPEND",
    )

    t3 = PubSubPublishCallableOperator(
        topic="composer-demo",
        task_id="publish-pubsub-notification",
        python_callable=get_pubsub_messages,
    )

    t1 >> t2 >> t3
