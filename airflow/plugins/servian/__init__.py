from airflow.plugins_manager import AirflowPlugin

from servian import operators


class Servian(AirflowPlugin):
    """
    This plugin provides HTTP hooks for Airflow with
    enhanced functionality. E.g. they allow for specifying
    authentication information other than Basic Auth
    and enable simple reading of paginated endpoints.
    """

    name = "servian"
    operators = [operators.PubSubPublishCallableOperator]
