from typing import Callable, Optional

class ConsumerData:
    def __init__(self, queue: str, topic: str, handler: Callable, dlq_handler: Optional[Callable] = None, auto_ack: bool = False):
        self.queue = queue
        self.topic = topic
        self.handler = handler
        self.dlq_handler = dlq_handler
        self.auto_ack = auto_ack