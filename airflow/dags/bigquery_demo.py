import json
import time
from base64 import b64encode
from datetime import timedelta

import airflow
from airflow import DAG

from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.operators.bash_operator import BashOperator
from servian.operators import PubSubPublishCallableOperator
from airflow.contrib.hooks.gcp_pubsub_hook import PubSubHook


# def success_callback(context):
#     hook = PubSubHook(gcp_conn_id=self.gcp_conn_id,
#                         delegate_to=self.delegate_to)
#     hook.publish(self.project, self.topic, self.messages)


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
    "email": ["chris.tippett@servian.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "project": "gcp-batch-pattern",
    "location": "US",
}

with DAG(
    "bigquery_demo",
    default_args=default_args,
    description="A simple tutorial DAG",
    schedule_interval=None,  # "*/5 * * * *",  # every 5 minutes
) as dag:

    t1 = BigQueryOperator(
        task_id="truncate-old-records",
        sql="""
            DELETE FROM `gcp-batch-pattern.composer_demo.demo_counter`
            WHERE inserted_ts < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 MINUTE)
        """.strip(),
        use_legacy_sql=False,
    )

    t2 = BigQueryOperator(
        task_id="append-counter-record",
        sql="""
            SELECT
                MAX(counter) + 1 AS counter,
                CURRENT_TIMESTAMP() AS inserted_ts,
                '{{ run_id }}' AS dag_run_id
            FROM
                `gcp-batch-pattern.composer_demo.demo_counter`
        """.strip(),
        use_legacy_sql=False,
        destination_dataset_table="composer_demo.demo_counter",
        write_disposition="WRITE_APPEND",
    )

    t3 = PubSubPublishCallableOperator(
        topic="composer-demo",
        task_id="publish-pubsub-notification",
        python_callable=get_pubsub_messages,
    )

    t4 = BigQueryOperator(
        task_id="select-from-bigquery-1",
        sql="SELECT 1 AS test_data",
        use_legacy_sql=False,
        location="US",
    )

    t5 = BigQueryOperator(
        task_id="select-from-bigquery-2",
        sql="SELECT 2 AS test_data",
        use_legacy_sql=False,
        location="US",
    )

    t6 = BigQueryOperator(
        task_id="insert-counter-record",
        sql="""

            INSERT `gcp-batch-pattern.composer_demo.demo_counter` (counter, inserted_ts, dag_run_id)
            SELECT
                MAX(counter) + 1 AS counter,
                CURRENT_TIMESTAMP() AS inserted_ts,
                '{{ run_id }}' AS dag_run_id
            FROM
                `gcp-batch-pattern.composer_demo.demo_counter`
        """.strip(),
        use_legacy_sql=False,
    )

    t7 = BigQueryOperator(
        task_id="select-from-bigquery-3",
        sql="SELECT aiwhdiwuadaiwudhawiud111 AS &&;;;1421425%%%",
        use_legacy_sql=False,
        location="US",
    )

    t1 >> t2 >> t3

    t1 >> t4 >> t5 >> t3

    t6 >> t7
