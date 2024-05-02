import time
from celery import Celery
from typing import Optional

from hijiki.broker.broker_data import get_broker_url, init_os_environ


class HijikiBroker:
    celery_broker = None

    def __init__(self, app_name, host, username, password, port, cluster_hosts, heartbeat: Optional[float] = 60):
        init_os_environ(host, username, password, port, cluster_hosts)
        self.celery_broker = Celery(app_name, broker=get_broker_url(), set_as_current=True, heartbeat=heartbeat)

    def get_celery_broker(self):
        return self.celery_broker

    def ping(self):
        try:
            success_ping = False
            inspect = self.celery_broker.control.inspect()
            for i in range(4):
                try:
                    inspect.ping()
                    success_ping = True
                    break
                except BrokenPipeError as e:
                    time.sleep(0.10)
                    print("Celery worker connection failed. Reattempting")
                    if i == 3:
                        print("Failed to connect to celery due to a BrokenPipeError")
                        print(e)
            return success_ping
        except Exception as e:
            print("Failed to start broker")
            print(e)
            return False
