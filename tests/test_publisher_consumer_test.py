import time
import unittest

from hijiki.publisher.Publisher import Publisher
from tests.runner import Runner

DLQ_RETRY_NUMBER = 11 # At eleven interaction the message goes to the Dead Letter Queue
SECS_TO_AWAIT_BROKER = 5
DLQ_DONT_RECEIVE_ERROR_WITH_AUTO_ACK_ENABLED = 1


class TestPublisherConsumer(unittest.TestCase):
    runner = None

    def setUp(self):
        self.runner = Runner()
        self.runner.run()
        self.pub = Publisher("localhost", "user", "pwd", 5672, heartbeat=30)
        self.NUMBER_OF_QUEUED_MESSAGES = 2

    def tearDown(self):
        self.runner.stop()

    def test_publish_a_message(self):
        self.runner.clear_results()
        self.pub.publish_message('teste1_event', '{"value": "This is the message"}')

    def test_consume_a_message(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.pub.publish_message('teste1_event', '{"value": "This is the message"}')
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(len(self.runner.get_results()), 1)

    def test_consume_a_message_with_other_mapper(self):
        self.runner.clear_results()
        def other_message_mapper(event_name: str, data: str):
            return {"other_key": data, "event_name": event_name}

        event_name = 'teste1_event'
        message = '{"value": "This is the message"}'
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.pub.publish_message(event_name, message, message_mapper=other_message_mapper)
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(self.runner.get_results_data(), [
            {"other_key": message, "event_name": event_name}
        ])

    def test_consume_a_message_failed(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.pub.publish_message('erro_event', '{"value": "This is the message"}')
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(DLQ_RETRY_NUMBER, len(self.runner.get_results()))

    def test_consume_a_message_failed_with_auto_ack_dont_go_to_DLQ(self):
        self.runner.clear_results()
        self.runner.set_auto_ack(True)
        try:
            time.sleep(SECS_TO_AWAIT_BROKER)
            self.pub.publish_message('erro_event', '{"value": "This is the message"}')
            time.sleep(SECS_TO_AWAIT_BROKER)
            self.assertEqual(DLQ_DONT_RECEIVE_ERROR_WITH_AUTO_ACK_ENABLED, len(self.runner.get_results()))
        finally:
            self.runner.set_auto_ack(False)

    def test_consume_a_message_dlq(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        for number in range(self.NUMBER_OF_QUEUED_MESSAGES):
            self.pub.publish_message(
                'erro_event',
                f'{{"value": "This is message number {number} that will be sent to dlq"}}'
            )

        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(self.NUMBER_OF_QUEUED_MESSAGES, len(self.runner.get_results_dlq()))

    def test_consume_a_message_without_consumer_dlq(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        for number in range(self.NUMBER_OF_QUEUED_MESSAGES):
            self.pub.publish_message(
                'without_dlq',
                '{"value": "This is the message that will fall into a dlq queue, which has no consumer"}'
            )
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(
            self.NUMBER_OF_QUEUED_MESSAGES * DLQ_RETRY_NUMBER,
            len(self.runner.get_results())
        )

    def test_consume_a_message_with_specific_routing_key(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.pub.publish_message('teste1_event', '{"value": "This is the message"}')
        self.pub.publish_message('teste1_event', '{"value": "This is the message"}', routing_key='specific_routing_key')
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(len(self.runner.get_result_for_specific_routing_key()), 1)
        self.assertEqual(len(self.runner.get_results_data()), 3) # são tres mensagens, pois a fila teste1_event recebe dois por causa do routing key coring "*"


