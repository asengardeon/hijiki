import logging
import threading
from typing import Callable, Optional

from hijiki.rabbitmq_adapter import RabbitMQAdapter
from hijiki.rabbitmq_connection import ConnectionParameters


class ConsumerRabbitMQAdapter(RabbitMQAdapter):
    def __init__(
        self,
        connection_params: ConnectionParameters,
        queue: str,
        topic: Optional[str],
        handler: Callable
    ):
        super().__init__(connection_params)
        self.queue = queue
        self.topic = topic or queue
        self.handler = handler

        self.create_exchange_and_queue()
        self._consumer_thread = None

    def create_exchange_and_queue(self):
        dlq_exchange = f"{self.queue}_DLQ"
        dlq_queue = f"{self.queue}_DLQ"

        self.get_channel().exchange_declare(exchange=dlq_exchange, exchange_type="fanout", durable=True)
        self.get_channel().queue_declare(queue=dlq_queue, durable=True, arguments={"x-queue-type": "quorum"})
        self.get_channel().queue_bind(queue=dlq_queue, exchange=dlq_exchange)

        queue_args = {
            "x-queue-type": "quorum",
            "x-dead-letter-exchange": dlq_exchange,
            "x-delivery-limit": 10
        }
        self.get_channel().queue_declare(queue=self.queue, durable=True, arguments=queue_args)

        if self.topic:
            self.get_channel().exchange_declare(exchange=self.topic, exchange_type='topic', durable=True)
            self.get_channel().queue_bind(queue=self.queue, exchange=self.topic, routing_key="*")

    def _consume(self):
        def callback(ch, method, properties, body):
            try:
                self.handler(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                yield
            except Exception as e:
                logging.error(f"Erro ao processar mensagem: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        self.get_channel().basic_consume(queue=self.queue, on_message_callback=callback)
        logging.info(f"Iniciando consumo na fila: {self.queue}")
        self.get_channel().start_consuming()
        yield

    def consume(self):
        """Inicia o consumo da fila em uma thread separada."""
        if self._consumer_thread and self._consumer_thread.is_alive():
            logging.warning("O consumidor já está rodando.")
            yield
            return
        self._consumer_thread = threading.Thread(target=self._consume, daemon=True)
        self._consumer_thread.start()
        logging.info(f"Thread de consumo iniciada para a fila: {self.queue}")
        yield



