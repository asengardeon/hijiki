from kombu import producers, Exchange

from hijiki.broker.hijiki_broker import HijikiBroker

client = HijikiBroker('client')
def publish_message(event_name: str, data: str):
    payload = {"value": data}
    connection = client.get_celery_broker().broker_connection()
    with producers[connection].acquire(block=True) as producer:
        task_exchange = Exchange(event_name, type='topic')
        producer.publish(payload,  exchange=task_exchange, declare=[task_exchange], routing_key='x')
