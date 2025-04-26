import unittest
from unittest.mock import patch, Mock, MagicMock

import pika

from hijiki.message_manager_builder import MessageManagerBuilder

DLQ_RETRY_NUMsBER = 11 # At eleven interaction the message goes to the Dead Letter Queue
SECS_TO_AWAIT_BROKER = 5


class TestBrokerPing(unittest.TestCase):

    @patch("pika.BlockingConnection", spec=pika.BlockingConnection)
    def test_success_ping(self, mock_pika):
        mock_pika.return_value = Mock()
        mock_pika.is_open.return_value = True
        manager = (MessageManagerBuilder.get_instance(recreate=True) \
            .with_user("user") \
            .with_password("pwd") \
            .with_host("localhost") \
            .with_port(5672) \
            .build())
        manager.broker.connection.connection = mock_pika
        self.assertTrue(manager.is_alive())

    @patch("pika.BlockingConnection", spec=pika.BlockingConnection)
    def test_fail_ping(self, mock_pika):
        mock_pika.return_value = Mock()
        mock_pika.is_open.return_value = False
        manager = MessageManagerBuilder.get_instance(recreate=True) \
            .with_user("user") \
            .with_password("wrong_pwd") \
            .with_host("localhost") \
            .with_port(5672) \
            .build()
        manager.broker.connection.connection = mock_pika
        self.assertFalse(manager.is_alive())
