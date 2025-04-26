import threading

from hijiki.consumer_data import ConsumerData
from hijiki.decorator import consumer_handler
from hijiki.message_manager_builder import MessageManagerBuilder

result_event_list = []
result_event_list_dlq = []

class Runner():
    # qs = [
    #     ConsumerData('teste1', 'teste1_event'),
    #     ConsumerData('fila_erro', 'erro_event'),
    #     ConsumerData('without_dlq', 'without_dlq'),
    # ]
    gr = MessageManagerBuilder()\
        .with_user("user") \
        .with_password("pwd") \
        .with_host("localhost") \
        .with_port(5672) \
        .build()

    threads = []


    @consumer_handler(queue_name="teste1")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
        result_event_list.append('received event')
    
    @consumer_handler(queue_name="teste1_dlq")
    def internal_consumer_dlq(data):
        print(f"consumiu o valor:{data}")
        result_event_list_dlq.append('received event')

    @consumer_handler(queue_name="fila_erro")
    def internal_consumer_erro(data):
        print(f"consumiu o valor:{data}")
        result_event_list.append('received event')
        raise Exception("falhou")

    @consumer_handler(queue_name="fila_erro_dlq")
    def internal_consumer_erro_dlq(data):
        print(f"consumiu o valor:{data}")
        result_event_list_dlq.append('received event')
    
    @consumer_handler(queue_name="without_dlq")
    def internal_consumer_extra(data):
        print(f"consumiu o valor:{data}")
        result_event_list.append('received event')
        raise Exception("falhou")


    def run(self):
        t = threading.Thread(target=self.gr.start_consuming())
        self.threads.append(t)
        t.start()

    def stop(self):
        self.gr.stop_consuming()

    def __del__(self):
        super()

    def clear_results(self):
        result_event_list.clear()
        result_event_list_dlq.clear()

    def get_results(self):
        return result_event_list

    def get_results(self):
        return result_event_list

    def get_results_dlq(self):
        return result_event_list_dlq

    def set_auto_ack(self, auto_ack: bool):
        self.gr.with_auto_ack(auto_ack)

    def publish_message(self, event_name, message):
        self.gr.publish(event_name, message)