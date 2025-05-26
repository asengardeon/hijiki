import logging
import threading
from typing import Callable, Optional

import pika  # Usando a biblioteca pika diretamente

from hijiki.rabbitmq_adapter import RabbitMQAdapter

class PublisherRabbitMQAdapter(RabbitMQAdapter):

    def publish(self, topic: str, message: str):
        self.get_channel().exchange_declare(exchange=topic, exchange_type='topic', durable=True)
        self.get_channel().basic_publish(
            exchange=topic,
            routing_key="*",
            body=str(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logging.info(f"Mensagem enviada para o tópico {topic}: {message}")
        yield