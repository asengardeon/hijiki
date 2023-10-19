import threading
import time
import unittest

from testcontainers.core.container import DockerContainer

from hijiki.broker.hijiki_rabbit import HijikiQueueExchange, HijikiRabbit
from hijiki.publisher.Publisher import Publisher

result_event_list = []
# container = (DockerContainer("rabbitmq:3-management-alpine").with_bind_ports(15672, 15672)
#              .with_bind_ports(5672, 5672)
#              .with_name("rabbit_test_container")
#              .with_env("RABBITMQ_DEFAULT_USER", "rabbitmq")
#              .with_env("RABBITMQ_DEFAULT_PASS","rabbitmq")).start()


class Runner():
    qs = [HijikiQueueExchange('teste1', 'teste1_event'), HijikiQueueExchange('teste2', 'teste2_event')]
    gr = HijikiRabbit().with_queues_exchange(qs) \
        .with_username("rabbitmq") \
        .with_password("rabbitmq") \
        .with_host("localhost") \
        .with_port(5672) \
        .build()

    threads = []

    @gr.task(queue_name="teste1")
    def internal_consumer(self):
        print("consumiu")
        result_event_list.append('recebeu evento')

    def run(self):
        t = threading.Thread(target=self.gr.run)
        self.threads.append(t)
        t.start()

    def __del__(self):
        super()


class TestPublisherConsumer(unittest.TestCase):
    runner = None

    def setUp(self):
        if not self.runner:
            self.runner = Runner()
            self.runner.run()
            self.pub = Publisher("localhost", "rabbitmq", "rabbitmq", 5672)

    def test_publish_a_message(self):
        self.pub.publish_message('teste1_event', '{"value": "Esta é a mensagem"}')

    def test_consume_a_message(self):
        self.pub = Publisher("localhost", "rabbitmq", "rabbitmq", 5672)
        time.sleep(5)
        self.pub.publish_message('teste1_event', '{"value": "Esta é a mensagem"}')
        time.sleep(1)
        self.assertEqual(len(result_event_list), 1)
