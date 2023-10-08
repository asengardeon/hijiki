import os
import unittest

from hijiki.broker.broker_data import get_broker_url, BROKER_SERVER, BROKER_USERNAME, BROKER_PWD, BROKER_PORT

class TestMyModule(unittest.TestCase):

    def setUp(self):
        os.environ[BROKER_SERVER] = 'teste'
    def tearDown(self):
        os.environ.pop(BROKER_SERVER) if os.environ.get(BROKER_SERVER) else None
        os.environ.pop(BROKER_USERNAME) if os.environ.get(BROKER_USERNAME) else None
        os.environ.pop(BROKER_PWD) if os.environ.get(BROKER_PWD) else None
        os.environ.pop(BROKER_PORT) if os.environ.get(BROKER_PORT) else None

    def test_broker_username_env_not_exists_in_environment_variable_but_server_exists(self):
        self.assertEqual(get_broker_url(), 'amqp://None:None@teste:5672')

    def test_broker_pwd_env_not_exists_in_environment_variable_but_server_exists(self):
        self.assertEqual(get_broker_url(), 'amqp://None:None@teste:5672')

    def test_broker_port_env_not_exists_in_environment_variable_but_server_exists(self):
        self.assertEqual(get_broker_url(), 'amqp://None:None@teste:5672')

    def test_broker_server_env_exists_in_environment_variable(self):
        self.assertEqual(get_broker_url(), 'amqp://None:None@teste:5672')

    def test_broker_server_env_exists_in_environment_variable(self):
        self.assertEqual(get_broker_url(), 'amqp://None:None@teste:5672')

    def test_alldata_env_exists_in_environment_variable(self):
        os.environ[BROKER_SERVER] = 'server'
        os.environ[BROKER_USERNAME] = 'usr'
        os.environ[BROKER_PWD] = 'password'
        os.environ[BROKER_PORT] = '5427'
        self.assertEqual(get_broker_url(), 'amqp://usr:password@server:5427')
