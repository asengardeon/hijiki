from hijiki.consumer_data import ConsumerData

from abc import ABC, abstractmethod

class MessageBroker(ABC):
    @abstractmethod
    def publish(self, topic: str, message: str):
        pass

    @abstractmethod
    def create_consumer(self, consumer_data: ConsumerData):
        pass

    @abstractmethod
    def start_consuming(self):
        pass
