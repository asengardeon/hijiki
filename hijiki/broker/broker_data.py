import os

def get_broker_url():
    server = os.environ["BROKER_SERVER"] if "BROKER_SERVER" in os.environ else None
    username = os.environ["BROKER_USERNAME"] if "BROKER_USERNAME" in os.environ else None
    pwd = os.environ["BROKER_PWD"] if "BROKER_PWD" in os.environ else None
    port = os.environ["BROKER_PORT"] if "BROKER_PORT" in os.environ else "5672"
    return f'amqp://{username}:{pwd}@{server}:{port}' if server else 'amqp://rabbitmq:rabbitmq@localhost:5672'