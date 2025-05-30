# message_manager.py
import json
from typing import Callable, Optional

from hijiki.ports.message_broker import MessageBroker
from hijiki.config.consumer_data import ConsumerData
import logging


def default_message_mapper(message: str, data: str):
    return {"value": data}

default_routing_key = 'x'


class MessageManager:
    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self.consumers = {}
        self.possible_consumers = []

    def publish(self, topic: str, message: str, message_mapper: Optional[Callable[[str, str], dict]]=default_message_mapper,
                        routing_key=default_routing_key):
        if message_mapper:
            payload = message_mapper(topic, message)
        else:
            payload = default_message_mapper(topic, message)
        new_message = json.dumps(payload)
        self.broker.publish(topic, new_message, routing_key)
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

    def define_broker(self, broker: MessageBroker):
        """Define o broker a ser usado pelo MessageManager."""
        self.broker = broker
        logging.info(f"Broker definido: {broker}")

    def is_alive(self):
        try:
           return self.broker.ping()
        except Exception:
            return False