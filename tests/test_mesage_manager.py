import unittest
from hijiki.message_manager import MessageManager
from hijiki.message_broker import MessageBroker
from hijiki.consumer_data import ConsumerData
from unittest.mock import Mock

class TestMessageManager(unittest.TestCase):
    def setUp(self):
        self.broker_mock = Mock(spec=MessageBroker)
        self.manager = MessageManager(self.broker_mock)

    def test_publish_message(self):
        self.manager.publish("test_topic", "test_message")
        self.broker_mock.publish.assert_called_with("test_topic", "test_message")

    def test_create_consumer(self):
        handler_mock = Mock()
        consumer_data = ConsumerData("test_queue", "test_topic", handler_mock)
        self.manager.create_consumer(consumer_data)
        self.assertIn("test_queue", self.manager.consumers)
        self.broker_mock.create_consumer.assert_called_with(consumer_data)

    def test_start_consuming(self):
        self.manager.start_consuming()
        self.broker_mock.start_consuming.assert_called()