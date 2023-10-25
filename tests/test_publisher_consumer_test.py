import threading
import time
import unittest

from hijiki.broker.hijiki_rabbit import HijikiQueueExchange, HijikiRabbit
from hijiki.publisher.Publisher import Publisher

result_event_list = []


class Runner():
    qs = [HijikiQueueExchange('teste1', 'teste1_event'), HijikiQueueExchange('teste2', 'teste2_event')]
    gr = HijikiRabbit().with_queues_exchange(qs) \
        .with_username("user") \
        .with_password("pwd") \
        .with_host("localhost") \
        .with_port(5672) \
        .build()

    threads = []

    @gr.task(queue_name="teste1")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
        result_event_list.append('recebeu evento')

    def run(self):
        t = threading.Thread(target=self.gr.run)
        self.threads.append(t)
        t.start()

    def stop(self):
        self.gr.terminate()

    def __del__(self):
        super()


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
        self.assertEqual(len(result_event_list), 1)
