# fastapi_example.py
from fastapi import FastAPI
from hijiki.message_manager_builder import MessageManagerBuilder
from hijiki.broker_type import BrokerType
from hijiki.decorator import consumer_handler
from hijiki.consumer_data import ConsumerData

app = FastAPI()
manager = (MessageManagerBuilder.get_instance()
           .with_broker_type(BrokerType.RABBITMQ)
           .with_host("localhost")
           .with_port(5672)
           .with_user("user")
           .with_password("pwd")
           .build())

@consumer_handler("test_queue")
def sample_handler(message):
    print(f"Received message: {message}")

consumer_data = ConsumerData("test_queue", "test_topic", sample_handler)
manager.create_consumer(consumer_data)
manager.start_consuming()

@app.post("/publish/")
def publish_message(topic: str, message: str):
    manager.publish(topic, message)
    return {"message": "Published successfully"}