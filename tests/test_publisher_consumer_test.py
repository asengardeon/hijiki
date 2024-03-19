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
        self.pub = Publisher("localhost", "user", "pwd", 5672)

    def tearDown(self):
        self.runner.stop()

    def test_publish_a_message(self):
        self.runner.clear_results()
        self.pub.publish_message('teste1_event', '{"value": "Esta é a mensagem"}')

    def test_consume_a_message(self):
        self.runner.clear_results()
        self.pub = Publisher("localhost", "user", "pwd", 5672)
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.pub.publish_message('teste1_event', '{"value": "Esta é a mensagem"}')
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(len(self.runner.get_results()), 1)

    def test_consume_a_message_failed(self):
        self.runner.clear_results()
        self.pub = Publisher("localhost", "user", "pwd", 5672)
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.pub.publish_message('erro_event', '{"value": "Esta é a mensagem"}')
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(DLQ_RETRY_NUMBER, len(self.runner.get_results()))


