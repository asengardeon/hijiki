from typing import Callable, Optional

from hijiki.config.consumer_data import ConsumerData
from hijiki.manager.message_manager_builder import MessageManagerBuilder


def consumer_handler(queue_name: str, topic: Optional[str] = None, routing_key: Optional[str] = None,
                     create_dlq=True) -> Callable:
    def decorator(func: Callable):
        consumer_data = ConsumerData(queue=queue_name, topic=topic or f"{queue_name}_event", handler=func, routing_key=routing_key, create_dlq=create_dlq)
        manager_builder =  MessageManagerBuilder.get_instance()
        if manager_builder:
            manager_builder.add_possible_consumer(consumer_data)
        return func
    return decorator

