import os
import unittest
from hijiki.connection.rabbitmq_connection import RabbitMQConnection, ConnectionParameters


class TestRabbitMQConnection(unittest.TestCase):

    def setUp(self):
        self.env_vars = {
            'BROKER_SERVER': 'env_host',
            'BROKER_PORT': '5673',
            'BROKER_USERNAME': 'env_user',
            'BROKER_PWD': 'env_password',
            'BROKER_CLUSTER_SERVER': 'env_host1,env_host2'
        }
        self.original_env = {key: os.environ.get(key) for key in self.env_vars}
        os.environ.update(self.env_vars)

    def tearDown(self):
        for key, value in self.original_env.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value

    def test_get_broker_url_from_env(self):
        os.environ.pop('BROKER_CLUSTER_SERVER')  # Garantir que apenas BROKER_SERVER está definido
        connection = RabbitMQConnection()
        expected_url = 'amqp://env_user:env_password@env_host:5673'
        self.assertEqual(connection.get_broker_url(), expected_url)

    def test_get_broker_url_from_env_with_cluster(self):
        os.environ.pop('BROKER_SERVER')  # Garantir que apenas BROKER_CLUSTER_SERVER está definido
        connection = RabbitMQConnection()
        expected_url = 'amqp://env_user:env_password@env_host1;amqp://env_user:env_password@env_host2'
        self.assertEqual(connection.get_broker_url(), expected_url)

    def test_get_broker_url_from_builder(self):
        os.environ.pop('BROKER_CLUSTER_SERVER')
        connection_parameters = ConnectionParameters(host='builder_host', port=5674, user='builder_user',
                           password='builder_password')
        connection = RabbitMQConnection(connection_parameters)
        expected_url = 'amqp://builder_user:builder_password@builder_host:5674'
        self.assertEqual(connection.get_broker_url(), expected_url)

    def test_get_broker_url_from_builder_with_cluster(self):
        os.environ.pop('BROKER_SERVER')  # Garantir que apenas BROKER_CLUSTER_SERVER está definido
        connection_parameters = ConnectionParameters(host=None, port=None, user=None, password=None,
                                        cluster_hosts='builder_host1,builder_host2')
        connection = RabbitMQConnection(connection_parameters)
        expected_url = 'amqp://env_user:env_password@builder_host1;amqp://env_user:env_password@builder_host2'
        self.assertEqual(connection.get_broker_url(), expected_url)

    def test_get_broker_url_from_builder_with_cluster_and_heartbeat(self):
        os.environ.pop('BROKER_SERVER')  # Garantir que apenas BROKER_CLUSTER_SERVER está definido
        connection_parameters = ConnectionParameters(host=None, port=None, user=None, password=None,
                                        cluster_hosts='builder_host1,builder_host2', extra_connection_params={"heartbeat":36})
        connection = RabbitMQConnection(connection_parameters)
        expected_url = 'amqp://env_user:env_password@builder_host1?heartbeat=36;amqp://env_user:env_password@builder_host2?heartbeat=36'
        self.assertEqual(connection.get_broker_url(), expected_url)

    def test_get_broker_url_from_builder_with_heartbeat(self):
        os.environ.pop('BROKER_CLUSTER_SERVER')
        connection_parameters = ConnectionParameters(host='builder_host', port=5674, user='builder_user',
                           password='builder_password', extra_connection_params={"heartbeat":37})
        connection = RabbitMQConnection(connection_parameters)
        expected_url = 'amqp://builder_user:builder_password@builder_host:5674?heartbeat=37'
        self.assertEqual(connection.get_broker_url(), expected_url)