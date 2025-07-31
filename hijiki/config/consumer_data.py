from typing import Callable, Optional

class ConsumerData:
    def __init__(self, queue: str, topic: str, handler: Callable, dlq_handler: Optional[Callable] = None,
                 routing_key: Optional[str] = "*", auto_ack: Optional[bool] = False, create_dlq:bool = True,
                 queue_type: Optional[str] = None, exchange_type: Optional[str] = None, dlq_name: Optional[str] = None,
                 dlx_name: Optional[str] = None, custom_queue_args: Optional[dict] = None):
        self.queue = queue
        self.topic = topic
        self.handler = handler
        self.dlq_handler = dlq_handler
        self.auto_ack = auto_ack
        self.routing_key = routing_key
        self.create_dlq = create_dlq
        self.queue_type = queue_type
        self.exchange_type = exchange_type
        self.dlq_name = dlq_name
        self.dlx_name = dlx_name
        self.custom_queue_args = custom_queue_args