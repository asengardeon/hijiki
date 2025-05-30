
from hijiki.config.broker_config import BrokerConfig
from hijiki.config.broker_type import BrokerType
from hijiki.config.consumer_data import ConsumerData
from hijiki.manager.message_manager import MessageManager
from hijiki.adapters.rabbitmq_broker import RabbitMQBroker
from hijiki.connection.rabbitmq_connection import ConnectionParameters


class MessageManagerBuilder:
    _instance = None  # Instância única do MessageManagerBuilder

    def __init__(self, recreate=False):
        if MessageManagerBuilder._instance is not None:
            if not recreate:
                # Se for para recriar, limpa a instância anterior
                raise ValueError("Apenas uma instância do MessageManager pode existir.")
            else:
                # Se for para recriar, limpa a instância anterior
                MessageManagerBuilder._instance = None
        else:
            broker_config = BrokerConfig()
            self.host = broker_config.get_host()
            self.port = broker_config.get_port()
            self.user = broker_config.get_user()
            self.password = broker_config.get_password()
            self.cluster_hosts = broker_config.get_cluster_hosts()
            self.consumers_data = []
            self.broker_type = BrokerType.RABBITMQ
            self.heartbeat_interval = 60 # 60 é o tempo, em segundos, padrão do RabbitMQ desde a versão 3.3.5
            self.manager = None
            MessageManagerBuilder._instance = self
            self.possible_consumers = []  # Lista de consumidores via decorator que podem ser registrados posteriormente.

    @staticmethod
    def get_instance(recreate=False):
        if MessageManagerBuilder._instance is None or recreate:
            MessageManagerBuilder(recreate)
        return MessageManagerBuilder._instance

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

    def with_consumers(self, consumers_data: list[ConsumerData]):
        self.consumers_data = consumers_data
        return self

    def with_broker_type(self, broker_type: BrokerType):
        self.broker_type = broker_type
        return self

    def with_heartbeat_interval(self, heartbeat_interval: int):
        self.heartbeat_interval = heartbeat_interval
        return self

    def add_possible_consumer(self, consumer_data: ConsumerData):
        self.possible_consumers.append(consumer_data)

    def build(self) -> MessageManager:
        extra_params = {
            'heartbeat': self.heartbeat_interval
        }
        connection_params = ConnectionParameters(self.host, self.port, self.user, self.password, self.cluster_hosts, extra_connection_params=extra_params)
        broker = RabbitMQBroker(connection_params) if self.broker_type == BrokerType.RABBITMQ else None
        if not broker:
            raise ValueError("BrokerType inválido ou não suportado.")

        if not MessageManagerBuilder._instance.manager:
            # Cria uma nova instância do MessageManager se não existir
            manager = MessageManager(broker)
            MessageManagerBuilder._instance.manager= manager
        else:
            MessageManagerBuilder._instance.manager.define_broker(broker)

        # Registra automaticamente todos os consumidores informados
        for consumer_data in self.possible_consumers:
            MessageManagerBuilder.get_instance().manager.create_consumer(consumer_data)

        # Registra automaticamente todos os consumidores informados
        for consumer_data in self.consumers_data:
            MessageManagerBuilder.get_instance().manager.create_consumer(consumer_data)

        return MessageManagerBuilder.get_instance().manager