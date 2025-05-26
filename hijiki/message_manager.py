# message_manager.py
from typing import Callable

from hijiki.message_broker import MessageBroker
from hijiki.consumer_data import ConsumerData
import logging

class MessageManager:
    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self.consumers = {}

    def __default_message_mapper(_: str, data: str):
        return {"value": data}

    def publish(self, topic: str, message: str, message_mapper: Callable[[str, str], dict]=__default_message_mapper):
        payload = message_mapper(topic, message)
        self.broker.publish(topic, payload)
        logging.info(f"Mensagem publicada no tópico {topic}: {message}")

    def create_consumer(self, consumer_data: ConsumerData):
        consumer_adapter = self.broker.create_consumer(consumer_data)
        self.consumers[consumer_data.queue] = consumer_adapter
        logging.info(f"Consumidor registrado para a fila {consumer_data.queue}")

    def start_consuming(self):
        self.broker.start_consuming()

    def stop_consuming(self):
        for consumer_data in self.consumers.values():
            if hasattr(consumer_data, 'stop_consuming') and callable(getattr(consumer_data, 'stop_consuming')):
                consumer_data.stop_consuming()

    def is_alive(self):
        try:
           return self.broker.ping()
        except Exception:
            return False