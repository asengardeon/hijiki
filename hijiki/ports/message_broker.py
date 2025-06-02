from hijiki.config.consumer_data import ConsumerData

from abc import ABC, abstractmethod

class MessageBroker(ABC):
    @abstractmethod
    def publish(self, topic: str, message: str, routing_key: str = 'x', message_mapper=None):
        pass

    @abstractmethod
    def create_consumer(self, consumer_data: ConsumerData):
        pass

    @abstractmethod
    def start_consuming(self):
        pass

    @abstractmethod
    def ping(self):
        pass