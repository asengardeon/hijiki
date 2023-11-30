import threading

from hijiki.broker.hijiki_rabbit import HijikiQueueExchange, HijikiRabbit

result_event_list = []

class Runner():
    qs = [HijikiQueueExchange('teste1', 'teste1_event'), HijikiQueueExchange('teste2', 'teste2_event')]
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
        result_event_list.append('recebeu evento')

    def run(self):
        t = threading.Thread(target=self.gr.run)
        self.threads.append(t)
        t.start()

    def stop(self):
        self.gr.terminate()

    def __del__(self):
        super()

    def get_results(self):
        return result_event_list