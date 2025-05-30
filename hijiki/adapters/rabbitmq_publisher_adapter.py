import logging
from typing import Optional

import pika  # Usando a biblioteca pika diretamente

from hijiki.adapters.rabbitmq_adapter import RabbitMQAdapter
from hijiki.connection.rabbitmq_connection import ConnectionParameters


class PublisherRabbitMQAdapter(RabbitMQAdapter):
    def __init__(self, connection_data: ConnectionParameters):
        super().__init__(connection_data)
        self.connect()

    def publish(self, topic: str, message: str, routing_key: Optional[str] = "x"):
        channel = self.get_channel()
        channel.exchange_declare(exchange=topic, exchange_type='topic', durable=True)
        channel.basic_publish(
            exchange=topic,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logging.info(f"Mensagem enviada para o tópico {topic}: {message}")