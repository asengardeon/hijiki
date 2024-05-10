from typing import Optional

from kombu import producers, Exchange

from hijiki.broker.hijiki_broker import HijikiBroker


class Publisher():

    def __init__(self, host, username, password, port, cluster_hosts: str = None, heartbeat: Optional[float] = 60):
        self.client = HijikiBroker('client', host, username, password, port, cluster_hosts, heartbeat=heartbeat)

    def publish_message(self, event_name: str, data: str):
        payload = {"value": data}
        connection = self.client.get_celery_broker().broker_connection(heartbeat=self.client.heartbeat)
        with producers[connection].acquire(block=True) as producer:
            task_exchange = Exchange(event_name, type='topic')
            producer.publish(payload,  exchange=task_exchange, declare=[task_exchange], routing_key='x')
