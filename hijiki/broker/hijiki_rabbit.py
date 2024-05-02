from functools import wraps, partial
from typing import List

from kombu import Queue, Exchange
from kombu.common import logger

from hijiki.broker.hijiki_broker import HijikiBroker
from hijiki.decorator.worker import Worker


class HijikiQueueExchange():
    def __init__(self, name, exchange_name):
        self.name = name
        self.exchange_name = exchange_name


class HijikiRabbit():
    queues = {}
    callbacks = {}
    _prefix = ""

    def __init__(self):
        self.connection = None
        self.broker = None
        self.host = None
        self.cluster_hosts = None
        self.password = None
        self.username = None
        self.queue_exchanges = None
        self.worker = None
        self.port = None
        self.heartbeat_interval = None

    def terminate(self):
        self.worker.should_stop = True

    def with_queues_exchange(self, queue_exchanges: List[HijikiQueueExchange]):
        self.queue_exchanges = queue_exchanges
        return self

    def with_username(self, username: str):
        self.username = username
        return self

    def with_password(self, password: str):
        self.password = password
        return self

    def with_host(self, host: str):
        self.host = host
        return self

    def with_cluster_hosts(self, hosts: str):
        self.cluster_hosts = hosts
        return self

    def with_port(self, port: str):
        self.port = port
        return self

    def ping(self):
        return self.broker.ping()

    def with_heartbeat_interval(self, heartbeat_interval: int):
        self.heartbeat_interval = heartbeat_interval
        return self

    def build(self):
        self.broker = HijikiBroker('worker', self.host, self.username, self.password, self.port, self.cluster_hosts)
        self.connection = self.broker.get_celery_broker().broker_connection(heartbeat=self.heartbeat_interval)
        self.init_queues()
        return self

    def init_queues(self, ):
        for q in self.queue_exchanges:
            name = q.name
            if name not in self.queues:
                self.queues[name] = []
                self.queues[name+ "_dlq"] = []
            if name not in self.callbacks:
                self.callbacks[name] = []
                self.callbacks[name + "_dlq"] = []

            logger.debug("Setting up %s" % name)
            routing_key = "*"

            task_exchange = Exchange(f'{q.exchange_name}', type='topic')
            task_exchange_dlq = Exchange(f'{q.exchange_name}_dlq', type='topic')

            queue = Queue(name,
                          task_exchange,
                          routing_key=routing_key,
                          queue_arguments={'x-queue-type': 'quorum', 'x-dead-letter-exchange': f'{q.exchange_name}_dlq',
                                           'x-delivery-limit': 10})

            queue.bind(self.connection).declare()

            queue_dlq = Queue(f'{name}_dlq',
                              task_exchange_dlq,
                              routing_key=routing_key,
                              queue_arguments={'x-queue-type': 'quorum'})

            queue_dlq.bind(self.connection).declare()

            self.queues[name].append(queue)
            self.queues[name + "_dlq"].append(queue_dlq)

    def _wrap_function(self, function, callback, queue_name, task=False):

        self.callbacks[queue_name].append(callback)

        # The function returned by the decorator don't really do
        # anything.  The process_msg callback added to the consumer
        # is what actually responds to messages  from the client
        # on this particular queue.

        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                pass

            return wrapper

        return decorate

    def task(self, func=None, *, queue_name=None):
        """Wrap around a function that should be a task.
        The client should not expect anything to be returned.

        """
        if func is None:
            return partial(self.task, queue_name=queue_name)

        def process_message(body, message):
            logger.debug("Processing function {!r} "
                         " in message: {!r} "
                         "with data {!r}".format(func.__name__,
                                                 message,
                                                 body))
            try:
                func(body)
            except Exception as e:
                logger.error("Problem processing task", exc_info=True)
                message.requeue()
            else:
                logger.debug("Ack'ing message.")
                message.ack()

        return self._wrap_function(
            func, process_message, queue_name, task=True)

    def run(self):
        consumers_without_callbacks = [
            key
            for (key, callbacks) in self.callbacks.items()
            if not callbacks
        ]

        for key in consumers_without_callbacks:
            self.callbacks.pop(key)
            self.queues.pop(key)

        try:
            self.worker = Worker(self.connection, self)
            self.worker.run()
        except KeyboardInterrupt:
            print('bye bye')
