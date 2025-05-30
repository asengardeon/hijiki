from typing import Callable, Optional

class ConsumerData:
    def __init__(self, queue: str, topic: str, handler: Callable, dlq_handler: Optional[Callable] = None,
                 routing_key: Optional[str] = "*", auto_ack: Optional[bool] = False, create_dlq:bool = True):
        self.queue = queue
        self.topic = topic
        self.handler = handler
        self.dlq_handler = dlq_handler
        self.auto_ack = auto_ack
        self.routing_key = routing_key
        self.create_dlq = create_dlq