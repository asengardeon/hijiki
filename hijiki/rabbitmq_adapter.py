import logging

from hijiki.rabbitmq_connection import ConnectionParameters, RabbitMQConnection


class RabbitMQAdapter:
    def __init__(self, connection_data: ConnectionParameters):
        self.connection_data = connection_data
        # Cria conexão e canal usando pika
        self.connection = RabbitMQConnection(host=connection_data.host, port=connection_data.port,
                                             user=connection_data.user, password=connection_data.password,
                                             cluster_hosts=connection_data.cluster_hosts)
        self.connection.connect()
        self.rabbit_connection = self.connection.connection


    def close(self):
        """Fecha o canal e a conexão com o RabbitMQ."""
        if self.get_channel().is_open:
            self.get_channel().close()
        if self.rabbit_connection.is_open:
            self.rabbit_connection.close()


    def stop_consuming(self):
        if self.get_channel().is_open:
            self.get_channel().stop_consuming()
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
        return self.rabbit_connection.channel()
