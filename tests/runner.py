from typing import Callable, Optional

from hijiki.decorator import consumer_handler
from hijiki.message_manager_builder import MessageManagerBuilder

result_event_list = []
result_data_list = []
result_event_list_dlq = []
result_data_list_dlq_for_specific_routing_key = []

class Runner():
    def __init__(self):
        self.gr = (MessageManagerBuilder.get_instance()\
            .with_user("user")\
            .with_password("pwd")\
            .with_host("localhost")\
            .with_port(5672)
            .build())
        self.threads = []


    @consumer_handler(queue_name="teste1")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
        result_data_list.append(data)
        result_event_list.append('received event')

    @consumer_handler(queue_name="teste1_dlq", create_dlq=False)
    def internal_consumer_dlq(data):
        print(f"consumiu o valor:{data}")
        result_event_list_dlq.append('received event')

    @consumer_handler(queue_name="fila_erro", topic="erro_event")
    def internal_consumer_erro(data):
        print(f"consumiu o valor:{data}")
        result_event_list.append('received event')
        raise Exception("falhou")

    @consumer_handler(queue_name="fila_erro_dlq", topic="fila_erro_dlq_event", create_dlq=False)
    def internal_consumer_erro_dlq(data):
        print(f"consumiu o valor:{data}")
        result_event_list_dlq.append('received event')

    @consumer_handler(queue_name="without_dlq", topic="without_dlq", create_dlq=False)
    def internal_consumer_extra(data):
        print(f"consumiu o valor:{data}")
        result_data_list.append(data)
        result_event_list.append('received event')
        raise Exception("falhou")

    @consumer_handler(queue_name="teste_with_specific_routing_key", topic='teste1_event',
                      routing_key="specific_routing_key")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
        result_data_list.append(data)
        result_data_list_dlq_for_specific_routing_key.append('received event')


    def run(self):
        self.gr.start_consuming()


    def stop(self):
        self.gr.stop_consuming()

    def __del__(self):
        super()

    def clear_results(self):
        result_event_list.clear()
        result_data_list.clear()
        result_event_list_dlq.clear()
        result_data_list_dlq_for_specific_routing_key.clear()

    def get_results(self):
        return result_event_list

    def get_result_for_specific_routing_key(self):
        return result_data_list_dlq_for_specific_routing_key

    def get_results_data(self):
        return result_data_list

    def get_results_dlq(self):
        return result_event_list_dlq

    def set_auto_ack(self, auto_ack: bool):
        self.gr.with_auto_ack(auto_ack)

    def publish_message(self, event_name, message, routing_key="x", message_mapper: Optional[Callable[[str, str], dict]] = None):
        self.gr.publish(event_name, message, routing_key=routing_key, message_mapper=message_mapper)