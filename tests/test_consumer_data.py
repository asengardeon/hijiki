import unittest
from hijiki.consumer_data import ConsumerData
from unittest.mock import Mock


class TestConsumerData(unittest.TestCase):
    def test_consumer_data_initialization(self):
        handler_mock = Mock()
        dlq_handler_mock = Mock()
        consumer_data = ConsumerData("test_queue", "test_topic", handler_mock, dlq_handler_mock, auto_ack=True)

        self.assertEqual(consumer_data.queue, "test_queue")
        self.assertEqual(consumer_data.topic, "test_topic")
        self.assertEqual(consumer_data.handler, handler_mock)
        self.assertEqual(consumer_data.dlq_handler, dlq_handler_mock)
        self.assertTrue(consumer_data.auto_ack)