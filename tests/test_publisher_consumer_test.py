import time
import unittest

from hijiki.publisher.Publisher import Publisher
from tests.runner import Runner

DLQ_RETRY_NUMBER = 11 # At eleven interaction the message goes to the Dead Letter Queue
SECS_TO_AWAIT_BROKER = 5


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

    def test_consume_a_message_failed(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.pub.publish_message('erro_event', '{"value": "This is the message"}')
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(DLQ_RETRY_NUMBER, len(self.runner.get_results()))

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


