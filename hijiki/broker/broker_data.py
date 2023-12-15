import os

BROKER_PORT = "BROKER_PORT"
BROKER_PWD = "BROKER_PWD"
BROKER_USERNAME = "BROKER_USERNAME"
BROKER_SERVER = "BROKER_SERVER"
BROKER_CLUSTER_SERVER = "BROKER_CLUSTER_SERVER"


def __build_cluster_uri(cluster_server: str, username: str, pwd: str):
    servers = cluster_server.split(',')
    uri = ""
    for s in servers:
        uri += f'amqp://{username}:{pwd}@{s};'
    return uri


def get_broker_url():
    cluster_server = os.environ[BROKER_CLUSTER_SERVER] if BROKER_CLUSTER_SERVER in os.environ else None
    server = os.environ[BROKER_SERVER] if BROKER_SERVER in os.environ else None
    username = os.environ[BROKER_USERNAME] if BROKER_USERNAME in os.environ else None
    pwd = os.environ[BROKER_PWD] if BROKER_PWD in os.environ else None
    port = os.environ[BROKER_PORT] if BROKER_PORT in os.environ else "5672"
    if cluster_server:
        return __build_cluster_uri(cluster_server, username, pwd)
    else:
        return f'amqp://{username}:{pwd}@{server}:{port}' if server else 'amqp://rabbitmq:rabbitmq@localhost:5672'


def init_os_environ(host, username, password, port, cluster_servers):
    if cluster_servers:
        os.environ[BROKER_CLUSTER_SERVER] = cluster_servers
    if host:
        os.environ[BROKER_SERVER] = host
    if username:
        os.environ[BROKER_USERNAME] = username
    if password:
        os.environ[BROKER_PWD] = password
    if port:
        os.environ[BROKER_PORT] = str(port)
