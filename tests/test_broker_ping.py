import unittest

from hijiki.broker.hijiki_broker import HijikiBroker
from tests.runner import Runner

DLQ_RETRY_NUMBER = 11 # At eleven interaction the message goes to the Dead Letter Queue
SECS_TO_AWAIT_BROKER = 5


class TestBrokerPing(unittest.TestCase):
    runner = None

    def setUp(self):
        self.runner = Runner()
        self.runner.run()

    def tearDown(self):
        self.runner.stop()

    def test_success_ping(self):
        broker = HijikiBroker("worker", "localhost", "user", "pwd", 5672, None)
        self.assertTrue(broker.ping())

    def test_fail_ping(self):
        broker = HijikiBroker("worker", "localhost", "user", "wrong_pwd", 5672, None)
        self.assertFalse(broker.ping())
