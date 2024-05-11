import time
from celery import Celery
from typing import Optional

from kombu import Connection, Exchange, Queue, Consumer

from hijiki.broker.broker_data import get_broker_url, init_os_environ


class HijikiBroker:
    celery_broker = None
    heartbeat = None

    def __init__(self, app_name, host, username, password, port, cluster_hosts, heartbeat: Optional[float] = 60):
        init_os_environ(host, username, password, port, cluster_hosts)
        self.heartbeat = heartbeat
        self.celery_broker = Celery(app_name, broker=get_broker_url(), set_as_current=True)


    def get_celery_broker(self):
        return self.celery_broker

    def ping(self):
        try:
            success_ping = False
            rabbit_url = get_broker_url()
            conn = Connection(rabbit_url)
            try:
                exchange = Exchange("ping-exchange", type="direct")
                queue = Queue(name="ping-queue", exchange=exchange, routing_key="Pong")

                def process_message(body, message):
                    print("The body is {}".format(body))
                    message.ack()

                with Consumer(conn, queues=queue, callbacks=[process_message], accept=["text/plain"]):
                    success_ping = True
            finally:
                conn.close()
            return success_ping
        except Exception as e:
            print("Failed to start broker")
            print(e)
            return False
