from celery import Celery

from hijiki.broker.broker_data import get_broker_url, init_os_environ


class HijikiBroker:
    celery_broker = None

    def __init__(self, app_name, host, username, password, port, cluster_hosts):
        init_os_environ(host, username, password, port, cluster_hosts)
        self.celery_broker = Celery(app_name, broker=get_broker_url(), set_as_current=True)

    def get_celery_broker(self):
        return self.celery_broker
