import logging

from hijiki.connection.rabbitmq_connection import ConnectionParameters, RabbitMQConnection


class RabbitMQAdapter:
    def __init__(self, connection_data: ConnectionParameters):
        self.rabbit_connection = None
        self.connection = None
        self.connection_data = connection_data
        self.channel = None

    def connect(self):
        # Cria conexão e canal usando pika
        self.connection = RabbitMQConnection(self.connection_data)
        self.connection.connect()
        self.rabbit_connection = self.connection.connection

    def stop_consuming(self):
        if self.channel.is_open:
            self.channel.close()


    def ping(self):
        """Verifica se a conexão está ativa."""
        result = False
        try:
            if self.rabbit_connection and self.rabbit_connection.is_open():
                self.rabbit_connection.process_data_events()
                result = True
        except Exception as e:
            logging.error(f"Erro ao verificar a conexão: {e}")
            result = False
        return result

    def get_channel(self):
        if not self.rabbit_connection or not self.rabbit_connection.is_open:
            self.connect()
        if not self.channel or not self.channel.is_open:
            self.channel = self.rabbit_connection.channel()
            self.channel.basic_qos(prefetch_count=1)
        return self.channel
