
import logging
from typing import Optional

from hijiki.config.consumer_data import ConsumerData
from hijiki.ports.message_broker import MessageBroker
from hijiki.adapters.rabbitmq_consumer_adapter import ConsumerRabbitMQAdapter
from hijiki.adapters.rabbitmq_publisher_adapter import PublisherRabbitMQAdapter
from hijiki.connection.rabbitmq_connection import RabbitMQConnection

class RabbitMQBroker(MessageBroker):
    def __init__(self, connection_params):
        self.publisher = None
        self.connection_params = connection_params
        self.consumers = {}

    def publish(self, topic: str, message: str, routing_key: str = 'x', exchange_type: Optional[str] = "topic",
                reply_to: Optional[str] = None):
        publisher = PublisherRabbitMQAdapter(self.connection_params)
        publisher.publish(topic, message, routing_key, exchange_type, reply_to)

    def create_consumer(self, consumer_data: ConsumerData):
        if consumer_data.handler:
            adapter = ConsumerRabbitMQAdapter(self.connection_params, consumer_data)
            self.consumers[consumer_data.queue] = adapter
            logging.info(f"Consumidor criado para a fila {consumer_data.queue} e tópico {consumer_data.topic or consumer_data.queue}")
            return adapter
        else:
            consumer_adapter = self.consumers[consumer_data.queue]
            consumer_adapter.queue_declare(queue=consumer_data.queue, durable=True)
            logging.info(f"Fila {consumer_data.queue} criada sem handler.")
            return None

    def start_consuming(self):
        """Inicia o consumo das filas registradas"""
        for consumer in self.consumers.values():
            consumer.consume()

    def ping(self):
        if not self.publisher and not len(self.consumers.values()):
            try:
                connection = RabbitMQConnection(self.connection_params)
                conn = connection.connect()
                conn.close()
                return True
            except Exception as e:
                logging.error(f"RabbitMQ ping failed: {e}")
                return False

        result = True
        for consumer in self.consumers.values():
            result = result and consumer.ping()
        publisher_result = self.publisher.ping() if self.publisher else True
        result = result and publisher_result
        return result
