
import logging
from typing import Callable

from hijiki.rabbitmq_connection import RabbitMQConnection


class RabbitMQAdapter:
    def __init__(self, connection: RabbitMQConnection, queue: str, topic: Optional[str], handler: Callable):
        self.connection = connection
        self.queue = queue
        self.topic = topic or queue
        self.handler = handler
        self.channel = connection.get_channel()
        self.create_exchange_and_queue()

    def create_exchange_and_queue(self):
        """Cria o Exchange do tipo 'topic', a fila como quorum e a DLQ."""
        dlq_exchange = f"{self.queue}_DLQ"
        dlq_queue = f"{self.queue}_DLQ"

        self.channel.exchange_declare(exchange=dlq_exchange, exchange_type="fanout", durable=True)
        self.channel.queue_declare(queue=dlq_queue, durable=True, arguments={"x-queue-type": "quorum"})
        self.channel.queue_bind(queue=dlq_queue, exchange=dlq_exchange)

        queue_args = {
            "x-queue-type": "quorum",
            "x-dead-letter-exchange": dlq_exchange,
            "x-delivery-limit": 10
        }
        self.channel.queue_declare(queue=self.queue, durable=True, arguments=queue_args)

        if self.topic:
            self.channel.exchange_declare(exchange=self.topic, exchange_type='topic', durable=True)
            self.channel.queue_bind(queue=self.queue, exchange=self.topic, routing_key="*")

    def consume(self):
        """Inicia o consumo da fila, utilizando o handler para processar as mensagens."""

        def callback(ch, method, properties, body):
            try:
                self.handler(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.error(f"Erro ao processar mensagem: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        self.channel.basic_consume(queue=self.queue, on_message_callback=callback)
        logging.info(f"Iniciando consumo na fila: {self.queue}")
        self.channel.start_consuming()

    def stop_consuming(self):
        """Interrompe o consumo da fila."""
        if self.channel.is_open:
            self.channel.stop_consuming()
            logging.info(f"Consumo interrompido para a fila: {self.queue}")