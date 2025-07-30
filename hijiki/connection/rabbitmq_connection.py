import logging

import pika
from typing import Optional

from hijiki.config.broker_config import BrokerConfig


class ConnectionParameters:
    def __init__(self, host: str = None, port: int = None, virtual_host: str = None, user: str = None,
                 password: str = None, cluster_hosts: str="", use_secure_protocol: bool = False, extra_connection_params: Optional[dict] = None):
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.user = user
        self.password = password
        self.cluster_hosts = cluster_hosts
        self.use_secure_protocol = use_secure_protocol
        self.extra_connection_params = extra_connection_params or {}

    def __str__(self):
        return f"ConnectionParameters(host={self.host}, port={self.port}, virtual_host={self.virtual_host}, user={self.user}, password=****, cluster_hosts={self.cluster_hosts})"

class RabbitMQConnection:
    def __init__(self, connection_params: ConnectionParameters = None):
        """Inicializa a conexão com o RabbitMQ usando um objeto ConnectionParameters."""
        self.host = connection_params.host if connection_params and connection_params.host else BrokerConfig.get_host()
        self.port = connection_params.port if connection_params and connection_params.port else BrokerConfig.get_port()
        self.virtual_host = f"/{connection_params.virtual_host}" if connection_params and connection_params.virtual_host else ""
        self.user = connection_params.user if connection_params and connection_params.user else BrokerConfig.get_user()
        self.password = connection_params.password if connection_params and connection_params.password else BrokerConfig.get_password()
        self.cluster_hosts = connection_params.cluster_hosts if connection_params and connection_params.cluster_hosts else BrokerConfig.get_cluster_hosts()
        self.extra_connection_params = connection_params.extra_connection_params if connection_params and connection_params.extra_connection_params else {}
        self.use_secure_protocol = connection_params.use_secure_protocol if connection_params and connection_params.use_secure_protocol else False
        self.connection = None

    def __validate_host(self):
        if self.host and self.cluster_hosts:
            raise Exception("BROKER_HOST e BROKER_CLUSTER_SERVER são mutuamente exclusivos e não podem os dois estarem definidos")

    def _get_connecttion_url_params(self) -> str:
        result = "?"
        for key, value in self.extra_connection_params.items():
           result += f"{key}={value}&"
        return result[:-1]  # Remove o último '&'

    def get_broker_url(self) -> str:
        self.__validate_host()
        """Gera a URL de conexão para o broker."""
        url_connectio_params = self._get_connecttion_url_params()
        protocol = "amqps" if self.use_secure_protocol else "amqp"
        if self.cluster_hosts:
            cluster = self.cluster_hosts.split(",")
            urls = [f"{protocol}://{self.user}:{self.password}@{host}{url_connectio_params}" for host in cluster]
            final_url = ";".join(urls)
            if self.virtual_host:
                final_url += f"{self.virtual_host}"
            return final_url
        else:
            return f"{protocol}://{self.user}:{self.password}@{self.host}:{self.port}{self.virtual_host}{url_connectio_params}"

    def connect(self):
        broker_url = self.get_broker_url()
        logging.info(f"Conectando ao RabbitMQ com a URL: {broker_url}")
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