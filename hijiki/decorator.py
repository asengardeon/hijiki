from typing import Callable, Optional

from hijiki.consumer_data import ConsumerData
from hijiki.message_manager_builder import MessageManagerBuilder


def consumer_handler(queue_name: str, topic: Optional[str] = None, routing_key: Optional[str] = None) -> Callable:
    def decorator(func: Callable):
        consumer_data = ConsumerData(queue=queue_name, topic=topic or f"{queue_name}_event", handler=func, routing_key=routing_key)
        manager_builder =  MessageManagerBuilder.get_instance()
        if manager_builder:
            manager_builder.add_possible_consumer(consumer_data)
        return func
    return decorator

