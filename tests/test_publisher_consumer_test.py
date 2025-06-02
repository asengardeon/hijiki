import json
import time
import unittest

from tests.runner import Runner

DLQ_RETRY_NUMBER = 11 # At eleven interaction the message goes to the Dead Letter Queue
SECS_TO_AWAIT_BROKER = 5
DLQ_DONT_RECEIVE_ERROR_WITH_AUTO_ACK_ENABLED = 1

def default_message_mapper(event_name: str, data: str):
    return {"value": data}


class TestPublisherConsumer(unittest.TestCase):
    runner = None

    @classmethod
    def setUpClass(cls):
        cls.runner = Runner()
        cls.runner.run()
        cls.NUMBER_OF_QUEUED_MESSAGES = 2  # Já estava definido na linha anterior, só conferindo duplicidade
        cls.test_count = 0

    @classmethod
    def tearDownClass(cls):
        if cls.test_count != 8:
            raise Exception(f"Expected 8 tests, but found {cls.test_count}. Please check the test cases.")

    def tearDown(self):
        self.runner.clear_results()


    def test_publish_a_message(self):
        self.runner.clear_results()
        self.runner.publish_message('teste1_event', '{"value": "This is the message"}')
        TestPublisherConsumer.test_count += 1

    def test_consume_a_message(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.runner.publish_message('teste1_event', '{"value": "This is the message"}')
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(len(self.runner.get_results()), 1)
        TestPublisherConsumer.test_count += 1

    def test_consume_a_message_with_other_mapper(self):
        self.runner.clear_results()
        def other_message_mapper(event_name: str, data: str):
            return {"other_key": data, "event_name": event_name}

        event_name = 'teste1_event'
        message = "This is the message"
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.runner.publish_message(event_name, message, message_mapper=other_message_mapper)
        time.sleep(SECS_TO_AWAIT_BROKER)
        data = self.runner.get_results_data()
        self.assertEqual(len(data), 1)
        json_data = json.loads(data[0])
        self.assertEqual(json_data['other_key'], message)
        self.assertEqual(json_data['event_name'], event_name)
        TestPublisherConsumer.test_count += 1

    def test_consume_a_message_failed(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.runner.publish_message('erro_event', '{"value": "This is the message"}')
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(DLQ_RETRY_NUMBER, len(self.runner.get_results()))
        TestPublisherConsumer.test_count += 1

    def test_consume_a_message_failed_with_auto_ack_dont_go_to_DLQ(self):
        self.runner.clear_results()
        self.runner.gr.consumers["fila_erro"].auto_ack = True
        try:
            time.sleep(SECS_TO_AWAIT_BROKER)
            self.runner.publish_message('erro_event', '{"value": "This is the message"}')
            time.sleep(SECS_TO_AWAIT_BROKER)
            self.assertEqual(DLQ_DONT_RECEIVE_ERROR_WITH_AUTO_ACK_ENABLED, len(self.runner.get_results()))
        finally:
            self.runner.gr.consumers["fila_erro"].auto_ack = False
        TestPublisherConsumer.test_count += 1


    def test_consume_a_message_dlq(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        for number in range(self.NUMBER_OF_QUEUED_MESSAGES):
            self.runner.publish_message(
                'erro_event',
                f'{{"value": "This is message number {number} that will be sent to dlq"}}'
            )

        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(self.NUMBER_OF_QUEUED_MESSAGES, len(self.runner.get_results_dlq()))
        TestPublisherConsumer.test_count += 1

    def test_consume_a_message_without_consumer_dlq(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        for number in range(self.NUMBER_OF_QUEUED_MESSAGES):
            self.runner.publish_message(
                'without_dlq',
                '{"value": "This is the message that will fall into a dlq queue, which has no consumer"}'
            )
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.assertEqual(
            self.NUMBER_OF_QUEUED_MESSAGES * DLQ_RETRY_NUMBER,
            len(self.runner.get_results())
        )
        TestPublisherConsumer.test_count += 1

    def test_consume_a_message_with_specific_routing_key(self):
        self.runner.clear_results()
        time.sleep(SECS_TO_AWAIT_BROKER)
        self.runner.publish_message('teste1_event', '{"value": "This is the message"}')
        self.runner.publish_message('teste1_event', '{"value": "This is the message"}', routing_key='specific_routing_key')
        time.sleep(SECS_TO_AWAIT_BROKER)
        print(self.runner.get_result_for_specific_routing_key())
        self.assertEqual(1, len(self.runner.get_result_for_specific_routing_key()))
        self.assertEqual(3, len(self.runner.get_results_data())) # são tres mensagens, pois a fila teste1_event recebe dois por causa do routing key coring "*"
        TestPublisherConsumer.test_count += 1
