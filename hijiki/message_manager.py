# message_manager.py
from hijiki.message_broker import MessageBroker
from hijiki.consumer_data import ConsumerData
import logging

class MessageManager:
    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self.consumers = {}

    def publish(self, topic: str, message: str):
        self.broker.publish(topic, message)
        logging.info(f"Mensagem publicada no tópico {topic}: {message}")

    def create_consumer(self, consumer_data: ConsumerData):
        self.broker.create_consumer(consumer_data)
        self.consumers[consumer_data.queue] = consumer_data
        logging.info(f"Consumidor registrado para a fila {consumer_data.queue}")

    def start_consuming(self):
        self.broker.start_consuming()
