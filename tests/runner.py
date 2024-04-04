import threading

from hijiki.broker.hijiki_rabbit import HijikiQueueExchange, HijikiRabbit

result_event_list = []
result_event_list_dlq = []

class Runner():
    qs = [
        HijikiQueueExchange('teste1', 'teste1_event'),
        HijikiQueueExchange('fila_erro', 'erro_event'),
        HijikiQueueExchange('without_dlq', 'without_dlq'),
    ]
    gr = HijikiRabbit().with_queues_exchange(qs) \
        .with_username("user") \
        .with_password("pwd") \
        .with_host("localhost") \
        .with_port(5672) \
        .build()

    threads = []

    @gr.task(queue_name="teste1")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
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
        result_event_list.append('received event')
        raise Exception("falhou")


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
        result_event_list_dlq.clear()

    def get_results(self):
        return result_event_list

    def get_results(self):
        return result_event_list

    def get_results_dlq(self):
        return result_event_list_dlq