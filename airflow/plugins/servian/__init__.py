from airflow.plugins_manager import AirflowPlugin

from servian import operators


class Servian(AirflowPlugin):
    name = "servian"
    operators = [operators.PubSubPublishCallableOperator]
