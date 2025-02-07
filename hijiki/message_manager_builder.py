
from hijiki.broker_config import BrokerConfig
from hijiki.broker_type import BrokerType
from hijiki.message_manager import MessageManager
from hijiki.rabbitmq_adapter import RabbitMQConnection
from hijiki.rabbitmq_broker import RabbitMQBroker


class MessageManagerBuilder:
    def __init__(self):
        broker_config = BrokerConfig()
        self.host = broker_config.get_host()
        self.port = broker_config.get_port()
        self.user = broker_config.get_user()
        self.password = broker_config.get_password()
        self.cluster_hosts = broker_config.get_cluster_hosts()
        self.consumers_data = []
        self.broker_type = BrokerType.RABBITMQ

    def with_host(self, host: str):
        self.host = host
        return self

    def with_port(self, port: int):
        self.port = port
        return self

    def with_user(self, user: str):
        self.user = user
        return self

    def with_password(self, password: str):
        self.password = password
        return self

    def with_cluster_hosts(self, cluster_hosts: str):
        self.cluster_hosts = cluster_hosts
        return self

    def with_consumers(self, consumers_data: list):
        self.consumers_data = consumers_data
        return self

    def with_broker_type(self, broker_type: BrokerType):
        self.broker_type = broker_type
        return self

    def build(self) -> MessageManager:
        connection = RabbitMQConnection(self.host, self.port, self.user, self.password, self.cluster_hosts)
        broker = RabbitMQBroker(connection) if self.broker_type == BrokerType.RABBITMQ else None
        if not broker:
            raise ValueError("BrokerType inválido ou não suportado.")
        return MessageManager(broker)