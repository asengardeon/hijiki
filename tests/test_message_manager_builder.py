import unittest
from unittest.mock import Mock, patch

from hijiki.config.broker_type import BrokerType
from hijiki.config.consumer_data import ConsumerData
from hijiki.manager.message_manager_builder import MessageManagerBuilder


class TestMessageManagerBuilder(unittest.TestCase):

    @patch("hijiki.adapters.rabbitmq_adapter.RabbitMQAdapter", autospec=True)
    @patch("pika.BlockingConnection", spec=True)
    def test_build_throws_error_with_invalid_broker_type(self, mock_pika, mock_adapter):
        mock_adapter.return_value = Mock()
        mock_pika.return_value = Mock()
        builder = MessageManagerBuilder.get_instance().with_broker_type("INVALID_BROKER")
        with self.assertRaises(ValueError):
            builder.build()

    @patch("hijiki.adapters.rabbitmq_adapter.RabbitMQAdapter", autospec=True)
    def test_singleton_instance_logic(self, mock_adapter):
        mock_adapter.return_value = Mock()
        instance1 = MessageManagerBuilder.get_instance()
        instance2 = MessageManagerBuilder.get_instance()
        self.assertIs(instance1, instance2)

    @patch("hijiki.adapters.rabbitmq_adapter.RabbitMQAdapter", autospec=True)
    @patch("hijiki.connection.rabbitmq_connection.ConnectionParameters", spec=True)
    def test_with_broker_type_rabbitmq_creates_rabbitmq_broker(self, mock_connection_params, mock_adapter):
        mock_adapter.return_value = Mock()
        mock_connection_params.return_value = Mock()
        builder = MessageManagerBuilder.get_instance().with_broker_type(BrokerType.RABBITMQ)
        manager = builder.build()
        self.assertIsNotNone(manager.broker)
        self.assertEqual(manager.broker.__class__.__name__, "RabbitMQBroker")

    @patch("hijiki.adapters.rabbitmq_adapter.RabbitMQAdapter", autospec=True)
    @patch("hijiki.connection.rabbitmq_connection.ConnectionParameters", spec=True)
    def test_with_consumers_registers_all_consumers(self, mock_connection_params, mock_adapter):
        mock_adapter.return_value = Mock()
        mock_connection_params.return_value = Mock()

        consumer1 = ConsumerData(queue="queue1", topic="topic1", handler=Mock())
        consumer2 = ConsumerData(queue="queue2", topic="topic2", handler=Mock())

        builder = (
            MessageManagerBuilder.get_instance()
            .with_consumers([consumer1, consumer2])
            .with_broker_type(BrokerType.RABBITMQ)
        )
        manager = builder.build()

        self.assertIn("queue1", manager.consumers)
        self.assertIn("queue2", manager.consumers)