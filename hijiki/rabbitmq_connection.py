import logging
from datetime import time

import pika
from typing import Optional

from hijiki.broker_config import BrokerConfig


class RabbitMQConnection:
    def __init__(self,
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 cluster_hosts: Optional[str] = None):
        """Inicializa a conexão com o RabbitMQ, usando valores passados ou variáveis de ambiente."""

        self.host = host or BrokerConfig.get_host()
        self.port = port or BrokerConfig.get_port()
        self.user = user or BrokerConfig.get_user()
        self.password = password or BrokerConfig.get_password()
        self.cluster_hosts = cluster_hosts or BrokerConfig.get_cluster_hosts()

        self.connection = None
        self.channel = None

    def get_broker_url(self) -> str:
        """Gera a URL de conexão para o broker."""
        if self.cluster_hosts:
            cluster = self.cluster_hosts.split(',')
            urls = [f'amqp://{self.user}:{self.password}@{host}' for host in cluster]
            return ';'.join(urls)
        else:
            return f'amqp://{self.user}:{self.password}@{self.host}:{self.port}'

    def connect(self):
        broker_url = self.get_broker_url()
        self.connection = pika.BlockingConnection(pika.URLParameters(broker_url))
        self.channel = self.connection.channel()
        logging.info("Conectado ao RabbitMQ")


    def get_channel(self):
        if not self.channel or self.connection.is_closed:
            self.connect()
        return self.channel

    def ping(self):
        try:
            if self.connection and self.connection.is_open:
                self.connection.process_data_events()
                return True
        except Exception:
            self.connect()
        return False