import unittest

import pika

from hijiki.message_manager_builder import MessageManagerBuilder
from hijiki.message_manager import MessageManager
from hijiki.broker_type import BrokerType
from unittest.mock import Mock, patch


class TestMessageManagerBuilder(unittest.TestCase):
    @patch("hijiki.rabbitmq_broker.RabbitMQBroker", autospec=True)
    @patch("pika.BlockingConnection", spec=pika.BlockingConnection)
    def test_build_message_manager(self, mock_broker, mock_pika):
        mock_broker.return_value = Mock()
        mock_pika.return_value = Mock()
        builder = (MessageManagerBuilder.get_instance()
                   .with_broker_type(BrokerType.RABBITMQ)
                   .with_host("localhost")
                   .with_port(5672)
                   .with_user("guest")
                   .with_password("guest"))
        manager = builder.build()
        self.assertIsInstance(manager, MessageManager)
        mock_broker.assert_called()