import json
import time
from base64 import b64encode
from datetime import timedelta

import airflow
from airflow import DAG

# from airflow.contrib.operators.pubsub_operator import PubSubPublishOperator
from airflow.operators.bash_operator import BashOperator
from servian.operators import PubSubPublishCallableOperator


def encode_pubsub_data(data):
    return b64encode(json.dumps(data).encode()).decode()


def get_pubsub_messages(**context):
    return [
        encode_pubsub_data(
            {
                "data": {
                    "inserted_ms": int(round(time.time() * 1000)),
                    "dag_run_id": context["dag_run"].run_id,
                }
            }
        )
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
    t1 = BashOperator(task_id="print_date", bash_command="date")

    t2 = BashOperator(task_id="sleep", depends_on_past=False, bash_command="sleep 5")

    t3 = PubSubPublishCallableOperator(
        topic="composer-demo",
        task_id="publish-pubsub-notification",
        python_callable=get_pubsub_messages,
    )

    t2.set_upstream(t1)
    t3.set_upstream(t1)
