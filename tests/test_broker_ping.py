import unittest
from unittest.mock import patch, Mock

import pika

from hijiki.config.consumer_data import ConsumerData
from hijiki.manager.message_manager_builder import MessageManagerBuilder

DLQ_RETRY_NUMsBER = 11 # At eleven interaction the message goes to the Dead Letter Queue
SECS_TO_AWAIT_BROKER = 5


class TestBrokerPing(unittest.TestCase):

    @patch("pika.BlockingConnection", spec=pika.BlockingConnection)
    def test_success_ping(self, mock_pika):
        mock_pika.return_value = Mock()
        mock_pika.is_open.return_value = True
        manager = (MessageManagerBuilder.get_instance() \
            .with_user("user") \
            .with_password("pwd") \
            .with_host("localhost") \
            .with_port(5672) \
            .build())
        consumer_data = ConsumerData("test_queue", "test_topic", handler=self.fail_ping_handler,
                                     dlq_handler=self.fail_ping_handler_dlq())
        manager.create_consumer(consumer_data)
        manager.start_consuming()

        for consumer in manager.broker.consumers.values():
            consumer.connection = mock_pika
        self.assertTrue(manager.is_alive())

    def fail_ping_handler(self):
        pass

    def fail_ping_handler_dlq(self):
        pass

    @patch("pika.BlockingConnection", spec=pika.BlockingConnection)
    def test_fail_ping(self, mock_pika):
        mock_pika.return_value = Mock()
        mock_pika.is_open.return_value = False
        manager = MessageManagerBuilder.get_instance() \
            .with_user("user") \
            .with_password("wrong_pwd") \
            .with_host("localhost") \
            .with_port(5672) \
            .build()
        consumer_data = ConsumerData("test_queue", "test_topic", handler=self.fail_ping_handler,
                                     dlq_handler=self.fail_ping_handler_dlq())
        manager.create_consumer(consumer_data)
        for consumer in manager.broker.consumers.values():
            consumer.connection = mock_pika
        self.assertFalse(manager.is_alive())
