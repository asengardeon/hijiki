from functools import wraps, partial, partialmethod
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
        self.worker = None

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

    def with_port(self, port: str):
        self.port = port
        return self

    def build(self):
        self.broker = HijikiBroker('worker', self.host, self.username, self.password, self.port)
        self.connection = self.broker.get_celery_broker().broker_connection()
        self.init_queues()
        return self

    def init_queues(self, ):
        for q in self.queue_exchanges:
            name = q.name
            if name not in self.queues:
                self.queues[name] = []
            if name not in self.callbacks:
                self.callbacks[name] = []

            logger.debug("Setting up %s" % name)
            routing_key = "*"

            task_exchange = Exchange(f'{q.exchange_name}', type='topic')
            task_exchange_dlq = Exchange(f'{q.exchange_name}_dlq', type='topic')

            queue = Queue(name,
                          task_exchange,
                          routing_key=routing_key,
                          queue_arguments={'x-queue-type': 'quorum','x-dead-letter-exchange': f'{q.exchange_name}_dlq', 'x-delivery-limit': 10})

            queue.bind(self.connection).declare()

            queue_dlq = Queue(f'{name}_dlq',
                          task_exchange_dlq,
                          routing_key=routing_key,
                          queue_arguments={'x-queue-type': 'quorum'})

            queue_dlq.bind(self.connection).declare()

            self.queues[name].append(queue)


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
            except Exception:
                logger.error("Problem processing task", exc_info=True)
            else:
                logger.debug("Ack'ing message.")
                message.ack()

        return self._wrap_function(
            func, process_message, queue_name, task=True)


    def run(self):
        try:
            self.worker = Worker(self.connection, self)
            self.worker.run()
        except KeyboardInterrupt:
            print('bye bye')