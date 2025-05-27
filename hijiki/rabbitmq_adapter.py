import logging

from hijiki.rabbitmq_connection import ConnectionParameters, RabbitMQConnection


class RabbitMQAdapter:
    def __init__(self, connection_data: ConnectionParameters):
        self.rabbit_connection = None
        self.connection = None
        self.connection_data = connection_data
        self.channel = None

    def close(self):
        """Fecha o canal e a conexão com o RabbitMQ."""
        if self.get_channel().is_open:
            self.get_channel().close()
        if self.rabbit_connection.is_open:
            self.rabbit_connection.close()

    def connect(self):
        # Cria conexão e canal usando pika
        self.connection = RabbitMQConnection(self.connection_data)
        self.connection.connect()
        self.rabbit_connection = self.connection.connection

    def stop_consuming(self):
        if self.channel.is_open:
            self.channel.stop_consuming()
            logging.info(f"Consumo interrompido para a fila: {self.queue}")
            self.close()


    def ping(self):
        """Verifica se a conexão está ativa."""
        try:
            if self.rabbit_connection and self.rabbit_connection.is_open():
                self.rabbit_connection.process_data_events()
                return True
        except Exception as e:
            logging.error(f"Erro ao verificar a conexão: {e}")
            return False

    def get_channel(self):
        if not self.rabbit_connection or not self.rabbit_connection.is_open:
            self.connect()
        if not self.channel or not self.channel.is_open:
            self.channel = self.rabbit_connection.channel()
        return self.channel
