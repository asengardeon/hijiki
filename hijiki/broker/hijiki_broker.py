import os

from celery import Celery
from kombu import Exchange, Queue

from hijiki.broker.broker_data import get_broker_url, init_os_environ


class HijikiBroker:
    celery_broker = None

    def bind_queues(self, queues_names):
        for name in queues_names:
            dlx = Exchange(f'dlq_{name}_exchange', type='topic')

            dead_letter_queue = Queue(f'dlq_{name}', dlx, routing_key='*', queue_arguments={'x-queue-type': 'quorum'})
            dead_letter_queue.bind(self.celery_broker.broker_connection()).declare()

    def __init__(self, app_name, host, username, password, port):
        init_os_environ(host, username, password, port)
        self.celery_broker = Celery(app_name, broker=get_broker_url(), set_as_current=True)


    def get_celery_broker(self):
        return self.celery_broker

    def bind_queues(self, queues_names):
        self.bind_queues(queues_names)