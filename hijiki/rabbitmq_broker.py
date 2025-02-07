
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
            # Cria o exchange (tópico) caso não exista
            self.channel.exchange_declare(exchange=topic, exchange_type='topic', durable=True)

            # Publica a mensagem no tópico
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
        """Cria e adiciona um consumidor, se houver handler, senão cria apenas o tópico e fila"""
        if consumer_data.handler:
            adapter = RabbitMQAdapter(self, consumer_data.queue, consumer_data.topic, consumer_data.handler)
            self.consumers[consumer_data.queue] = adapter
            logging.info(f"Consumidor criado para a fila {consumer_data.queue} e tópico {consumer_data.topic}")
            return adapter
        else:
            # Cria apenas o tópico e a fila
            self.channel.exchange_declare(exchange=consumer_data.topic, exchange_type='topic', durable=True)
            self.channel.queue_declare(queue=consumer_data.queue, durable=True)
            self.channel.queue_bind(queue=consumer_data.queue, exchange=consumer_data.topic, routing_key="*")
            logging.info(f"Tópico {consumer_data.topic} e fila {consumer_data.queue} criados.")
            return None

    def start_consuming(self):
        """Inicia o consumo das filas registradas"""
        for consumer in self.consumers.values():
            consumer.consume()
