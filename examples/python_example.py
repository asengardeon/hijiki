from hijiki.manager.message_manager_builder import MessageManagerBuilder
from hijiki.config.broker_type import BrokerType
from hijiki.decorators.decorator import consumer_handler
from hijiki.config.consumer_data import ConsumerData

def sample_handler(message):
    print(f"Received message: {message}")

manager = (MessageManagerBuilder().get_instance()
           .with_broker_type(BrokerType.RABBITMQ)
           .with_host("localhost")
           .with_port(5672)
           .with_user("guest")
           .with_password("guest")
           .build())

@consumer_handler("test_queue")
def decorated_handler(message):
    print(f"Processed message: {message}")

consumer_data = ConsumerData("test_queue", "test_topic", decorated_handler)
manager.create_consumer(consumer_data)
manager.start_consuming()


