import logging
import threading

from hijiki.config.consumer_data import ConsumerData
from hijiki.adapters.rabbitmq_adapter import RabbitMQAdapter
from hijiki.connection.rabbitmq_connection import ConnectionParameters


class ConsumerRabbitMQAdapter(RabbitMQAdapter):
    def __init__(self, connection_params: ConnectionParameters, consumer_data: ConsumerData):
        super().__init__(connection_params)
        self.queue = consumer_data.queue
        self.topic = consumer_data.topic or consumer_data.queue
        self.handler = consumer_data.handler
        self.auto_ack = consumer_data.auto_ack
        self.routing_key = consumer_data.routing_key if consumer_data.routing_key else "*"
        self._consumer_thread = None
        self.queue_type = consumer_data.queue_type
        self.exchange_type = consumer_data.exchange_type
        self.create_dlq = consumer_data.create_dlq
        self.dlq_name = consumer_data.dlq_name
        self.dlx_name = consumer_data.dlx_name
        self.custom_queue_args = consumer_data.custom_queue_args


    def create_exchange_and_queue(self):
        channel = self.get_channel()
        default_queue_args = { "x-delivery-limit": 10 }
        default_queue_type = "quorum"
        queue_args = (
            self.custom_queue_args
            if self.custom_queue_args is not None
            else default_queue_args
        )
        queue_args["x-queue-type"] = self.queue_type or default_queue_type

        default_exchange_type = "topic"
        exchange_type = self.exchange_type or default_exchange_type

        if self.create_dlq:
            if self.dlq_name:
                dlq_queue = self.dlq_name
            else:
                dlq_queue = f"{self.queue}_dlq" if not self.queue.endswith("_dlq") else self.queue

            if self.dlx_name:
                dlq_exchange = self.dlx_name
            else:
                dlq_exchange = f"{self.queue}_dlq_event" if not self.queue.endswith("_dlq") else f"{self.queue}_event"

            channel.exchange_declare(exchange=dlq_exchange, exchange_type=exchange_type, durable=True)
            channel.queue_declare(queue=dlq_queue, durable=True, arguments=queue_args)
            channel.queue_bind(queue=dlq_queue, exchange=dlq_exchange, routing_key=self.routing_key)

            queue_args["x-dead-letter-exchange"] = dlq_exchange
            channel.queue_declare(queue=self.queue, durable=True, arguments=queue_args)
        else:
            channel.queue_declare(queue=self.queue, durable=True, arguments=queue_args)

        if self.topic:
            channel.exchange_declare(exchange=self.topic, exchange_type=exchange_type, durable=True)
            channel.queue_bind(queue=self.queue, exchange=self.topic, routing_key=self.routing_key)

    def _consume(self):
        def callback(ch, method, properties, body):
            try:
                if self.auto_ack:
                    logging.info(f"Mensagem recebida na fila {self.queue}: {body.decode()}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                self.handler(body)
                if not self.auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.error(f"Erro ao processar mensagem: {e}")
                if not self.auto_ack:
                    ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

        try:
            self.get_channel().basic_consume(queue=self.queue, on_message_callback=callback)
            logging.info(f"Iniciando consumo na fila: {self.queue}")
            self.get_channel().start_consuming()
        except Exception as e:
            logging.error(f"Erro ao iniciar consumo com dados do adapter: {self.connection_data}")
            raise e

    def consume(self):
        self.connect()
        self.create_exchange_and_queue()
        """Inicia o consumo da fila em uma thread separada."""
        if self._consumer_thread and self._consumer_thread.is_alive():
            logging.warning("O consumidor já está rodando.")
            return
        self._consumer_thread = threading.Thread(target=self._consume, daemon=True)
        self._consumer_thread.start()
        logging.info(f"Thread de consumo iniciada para a fila: {self.queue}")
    

    def stop_consuming(self):
        def _stop_consuming():
            if self.get_channel().is_open:
                logging.info(f"Parando consumo da fila: {self.queue}")
                self.get_channel().stop_consuming()

        if self._consumer_thread and self._consumer_thread.is_alive():
            if self.rabbit_connection and self.rabbit_connection.is_open:
                self.rabbit_connection.add_callback_threadsafe(_stop_consuming)

            self._consumer_thread.join()
            super().stop_consuming()
