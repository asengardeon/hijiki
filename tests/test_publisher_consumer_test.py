import time
import unittest

from hijiki.publisher.Publisher import Publisher
from tests.runner import Runner


class TestPublisherConsumer(unittest.TestCase):
    runner = None

    def setUp(self):
        result_event_list = []
        self.runner = Runner()
        self.runner.run()
        self.pub = Publisher("localhost", "user", "pwd", 5672)

    def tearDown(self):
        self.runner.stop()

    def test_publish_a_message(self):
        self.pub.publish_message('teste1_event', '{"value": "Esta é a mensagem"}')

    def test_consume_a_message(self):
        self.pub = Publisher("localhost", "user", "pwd", 5672)
        time.sleep(5)
        self.pub.publish_message('teste1_event', '{"value": "Esta é a mensagem"}')
        time.sleep(1)
        self.assertEqual(len(self.runner.get_results()), 1)
