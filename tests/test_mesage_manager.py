import time
import unittest
from unittest.mock import Mock

from hijiki.adapters.rabbitmq_broker import RabbitMQBroker
from hijiki.config.consumer_data import ConsumerData
from hijiki.connection.rabbitmq_connection import ConnectionParameters
from hijiki.manager.message_manager_builder import MessageManagerBuilder
from hijiki.ports.message_broker import MessageBroker
from hijiki.manager.message_manager import MessageManager
import json

SECS_TO_AWAIT_BROKER = 2

def _other_message_mapper(event_name: str, data: str):
    return {"other_key": data, "event_name": event_name}


class TestMessageManager(unittest.TestCase):
    def setUp(self):
        self.broker_mock = Mock(spec=MessageBroker)
        self.manager = MessageManager(self.broker_mock)

    def test_publish_message(self):
        topic = "test_topic"
        message = "test_message"
        self.manager.publish(topic, message)
        self.broker_mock.publish.assert_called_with(topic, json.dumps({'value': 'test_message'}), 'x')

    def test_consume_a_message_with_other_mapper(self):
        event_name = 'teste1_event'
        message = "This is the message"
        self.manager.publish(event_name, message, message_mapper=_other_message_mapper)
        self.broker_mock.publish.assert_called_with(
            event_name,
            json.dumps(_other_message_mapper(event_name, message)),  # <- Aqui!
            'x'
        )

    def test_create_consumer(self):
        queue = "test_queue"
        topic = "test_topic"
        handler_mock = Mock()
        consumer_data = ConsumerData(queue, topic, handler_mock)
        self.manager.create_consumer(consumer_data)
        self.assertIn(queue, self.manager.consumers)
        self.broker_mock.create_consumer.assert_called_with(consumer_data)

    def test_start_consuming(self):
        self.manager.start_consuming()
        self.broker_mock.start_consuming.assert_called()

    def test_stop_consuming_rabbitmq_running_consumer(self):
        connection_params = ConnectionParameters("localhost", 5672, "user", "pwd")
        actual_broker = RabbitMQBroker(connection_params)
        manager = MessageManager(actual_broker)

        consumer_data = ConsumerData("test_queue", "test_topic", lambda x: x)
        manager.create_consumer(consumer_data)

        manager.start_consuming()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertTrue(manager.is_alive())

        manager.stop_consuming()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertFalse(manager.is_alive())