import os
from hijiki.broker_env_vars import BrokerEnvVars

class BrokerConfig:
    @staticmethod
    def get_host() -> str:
        return os.getenv(BrokerEnvVars.BROKER_SERVER)

    @staticmethod
    def get_port() -> int:
        return int(os.getenv(BrokerEnvVars.BROKER_PORT))

    @staticmethod
    def get_user() -> str:
        return os.getenv(BrokerEnvVars.BROKER_USERNAME)

    @staticmethod
    def get_password() -> str:
        return os.getenv(BrokerEnvVars.BROKER_PWD)

    @staticmethod
    def get_cluster_hosts() -> str:
        return os.getenv(BrokerEnvVars.BROKER_CLUSTER_SERVER)