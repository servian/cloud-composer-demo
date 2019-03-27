from airflow.exceptions import AirflowException
from airflow.contrib.operators.pubsub_operator import PubSubPublishOperator


class PubSubPublishCallableOperator(PubSubPublishOperator):
    def __init__(self, messages=None, python_callable=None, *args, **kwargs):
        if python_callable and not callable(python_callable):
            raise AirflowException('`python_callable` param must be callable')
        self.python_callable = python_callable
        super(PubSubPublishCallableOperator, self).__init__(
            messages=messages, *args, **kwargs
        )

    def execute(self, context):
        self.messages = self._get_messages(context)
        super(PubSubPublishCallableOperator, self).execute(context)

    def _get_messages(self, context):
        if self.messages is not None:
            return self.messages
        if self.python_callable is not None:
            return self.python_callable(context)
