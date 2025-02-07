
import logging

import pika

from hijiki.message_broker import MessageBroker
from hijiki.consumer_data import ConsumerData
from hijiki.rabbitmq_adapter import RabbitMQAdapter
from hijiki.rabbitmq_connection import RabbitMQConnection


class RabbitMQBroker(MessageBroker):
    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection
        self.channel = connection.get_channel()
        self.consumers = {}

    def publish(self, topic: str, message: str):
        try:
            self.channel.exchange_declare(exchange=topic, exchange_type='topic', durable=True)
            self.channel.basic_publish(
                exchange=topic,
                routing_key="*",
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logging.info(f"Mensagem enviada para o tópico {topic}: {message}")
        except Exception as e:
            logging.error(f"Erro ao publicar mensagem no tópico {topic}: {e}")

    def create_consumer(self, consumer_data: ConsumerData):
        if consumer_data.handler:
            adapter = RabbitMQAdapter(self.connection, consumer_data.queue, consumer_data.topic, consumer_data.handler)
            self.consumers[consumer_data.queue] = adapter
            logging.info(f"Consumidor criado para a fila {consumer_data.queue} e tópico {consumer_data.topic or consumer_data.queue}")
            return adapter
        else:
            self.channel.queue_declare(queue=consumer_data.queue, durable=True)
            logging.info(f"Fila {consumer_data.queue} criada sem handler.")
            return None
