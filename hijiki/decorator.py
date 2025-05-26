from typing import Callable, Optional

from hijiki.consumer_data import ConsumerData
from hijiki.message_manager_builder import MessageManagerBuilder


def consumer_handler(queue_name: str, topic: Optional[str] = None):
    def decorator(func: Callable):
        consumer_data = ConsumerData(queue=queue_name, topic=topic or f"{queue_name}_event", handler=func)
        manager = MessageManagerBuilder.get_instance().build()
        if manager:
            manager.create_consumer(consumer_data)
        return func
    return decorator

