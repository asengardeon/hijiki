# Hijiki
Python Rabbit wrapper library to simplify to use Exchanges and Queues with decorators

## Configurations
Hijiki uses environment variables to configure connection with BROKER. 

- BROKER_PORT
- BROKER_PWD
- BROKER_USERNAME
- BROKER_SERVER

If server is not present the connection url will be a default, and to others configs will be changed for "teste".

## How to use
### Publisher
The example demonstrate how to publish a simple message to topic "teste1_event" with a json message:

```python
pub = Publisher("localhost", "rabbitmq", "rabbitmq", 5672)
pub.publish_message('teste1_event', '{"value": "Esta é a mensagem"}')
```

### Consumer
Consumer uses a configuration to define QUEUES and Exchanges and the consumer is a decorator for the queue.

```python
from hijiki.broker.hijiki_rabbit import HijikiQueueExchange, HijikiRabbit

qs = [HijikiQueueExchange('teste1', 'teste1_event'), HijikiQueueExchange('teste2', 'teste2_event')]
gr = HijikiRabbit().with_queues_exchange(qs) \
    .with_username("rabbitmq") \
    .with_password("rabbitmq") \
    .with_host("localhost") \
    .with_port(5672) \
    .build()

class MyConsumer():
    @gr.task(queue_name='teste1')
    def my_consumer(data):
        print(f"consumer 1 executed with data : {data}")

    @gr.task(queue_name='teste2')
    def my_consumer2(data):
        print(f"consumer 2  executed with data : {data}")

if __name__ == '__main__':
    MyConsumer()
    gr.run()
```

