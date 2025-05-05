import threading

from hijiki.broker.hijiki_rabbit import HijikiQueueExchange, HijikiRabbit

result_event_list = []
result_data_list = []
result_event_list_dlq = []
result_data_list_dlq_for_specific_routing_key = []

class Runner():
    qs = [
        HijikiQueueExchange('teste1', 'teste1_event'),
        HijikiQueueExchange('fila_erro', 'erro_event'),
        HijikiQueueExchange('without_dlq', 'without_dlq'),
        HijikiQueueExchange('teste_with_specific_routing_key', 'teste1_event', routing_key='specific_routing_key'),
    ]
    gr = HijikiRabbit().with_queues_exchange(qs) \
        .with_username("user") \
        .with_password("pwd") \
        .with_host("localhost") \
        .with_port(5672) \
        .with_heartbeat_interval(30) \
        .build()

    threads = []


    @gr.task(queue_name="teste1")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
        result_data_list.append(data)
        result_event_list.append('received event')

    @gr.task(queue_name="teste1_dlq")
    def internal_consumer_dlq(data):
        print(f"consumiu o valor:{data}")
        result_event_list_dlq.append('received event')

    @gr.task(queue_name="fila_erro")
    def internal_consumer_erro(data):
        print(f"consumiu o valor:{data}")
        result_event_list.append('received event')
        raise Exception("falhou")

    @gr.task(queue_name="fila_erro_dlq")
    def internal_consumer_erro_dlq(data):
        print(f"consumiu o valor:{data}")
        result_event_list_dlq.append('received event')

    @gr.task(queue_name="without_dlq")
    def internal_consumer_extra(data):
        print(f"consumiu o valor:{data}")
        result_data_list.append(data)
        result_event_list.append('received event')
        raise Exception("falhou")

    @gr.task(queue_name="teste_with_specific_routing_key")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
        result_data_list.append(data)
        result_data_list_dlq_for_specific_routing_key.append('received event')


    def run(self):
        t = threading.Thread(target=self.gr.run)
        self.threads.append(t)
        t.start()

    def stop(self):
        self.gr.terminate()

    def __del__(self):
        super()

    def clear_results(self):
        result_event_list.clear()
        result_data_list.clear()
        result_event_list_dlq.clear()

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