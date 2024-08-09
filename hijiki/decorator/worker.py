import logging

from kombu.common import QoS
from kombu.mixins import ConsumerMixin

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Worker(ConsumerMixin):
    """Manage server side of RPC connection.

    This code is based on the examples on the Kombu website.
    """

    def __init__(self, connection, consumer):
        """Worker(connection)

        :connection: Connection object
        """
        self.prefetch = 0
        self.qos_initial_value = 0
        logger.debug("Called constructor. "
                     "Connection: {!r} Consumer {!r}"
                     .format(connection, consumer))
        logger.debug("Consumer has queues: {!r}".format(consumer.queues))
        self.connection = connection
        self.consumer = consumer

    def get_consumers(self, Consumer, channel):
        """Get a set of consumers.

        :Consumer: Consumer object
        :channel: a channel
        :returns: array of Consumer objects
        """
        consumer_set = []
        logger.info("called get_consumers with {!r}".format(self.consumer.queues))
        for i in self.consumer.queues.keys():
            queues = self.consumer.queues[i]
            callbacks = self.consumer.callbacks[i]
            logger.debug("Queues: {!r}".format(queues))
            c = Consumer(queues, callbacks=callbacks)
            if self.qos_initial_value != 0:
                qos = QoS(c.qos, initial_value=self.qos_initial_value)
                if self.prefetch != 0:
                    qos.set(self.prefetch)
                qos.update()  # set initial
            consumer_set.append(c)
            logger.info("Added consumer: {!r}".format(c))

        logger.info("Processed consumers {!r}".format(consumer_set))
        return consumer_set

    def set_prefetch(self, initial, value):
        self.qos_initial_value = initial
        self.prefetch = value
