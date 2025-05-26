import logging

import pika
from typing import Optional

from hijiki.broker_config import BrokerConfig

class ConnectionParameters:
    def __init__(self, host: str, port: int, user: str, password: str, cluster_hosts: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.cluster_hosts = cluster_hosts

    def __str__(self):
        return f"ConnectionParameters(host={self.host}, port={self.port}, user={self.user}, password=****, cluster_hosts={self.cluster_hosts})"

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

    def __validate_host(self):
        if self.host and self.cluster_hosts:
            raise Exception("BROKER_HOST e BROKER_CLUSTER_SERVER são mutuamente exclusivos e não podem os dois estarem definidos")

    def get_broker_url(self) -> str:
        self.__validate_host()
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
        logging.info("Conectado ao RabbitMQ")
        return self.connection


    def ping(self):
        try:
            if self.connection and self.connection.is_open():
                self.connection.process_data_events()
                return True
        except Exception:
            return False
        return False