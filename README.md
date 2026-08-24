# Hijiki

> Event-driven messaging for RabbitMQ, without the boilerplate.

[![PyPI](https://img.shields.io/pypi/v/hijiki)](https://pypi.org/project/hijiki/)
[![Python](https://img.shields.io/pypi/pyversions/hijiki)](https://pypi.org/project/hijiki/)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

🇧🇷 [Leia em português](README.pt-BR.md) · 📄 [v1 documentation](README_v1.md)

Hijiki is a high-level Python library for event-driven messaging on RabbitMQ. It
abstracts exchange declaration, queue binding, dead-letter queues and consumer
lifecycle behind a declarative API.

## Why

Every service in an event-driven architecture repeats the same setup: declare the
exchange, bind the queue, wire the dead-letter queue, keep the consumer alive.
Hijiki collapses that into a decorator — and creates the DLQ for you by default,
so resilience is the default rather than an extra step.

## Install

```shell
pip install hijiki
```

## Quick start

```python
from hijiki import MessageManagerBuilder, consumer_handler

manager = (
    MessageManagerBuilder()
    .with_host("localhost")
    .with_port(5672)
    .with_user("user")
    .with_password("pwd")
    .build()
)

@consumer_handler(queue_name="orders")
def handle_order(data):
    print(f"received: {data}")

manager.start_consuming()
```

That is the whole setup. The queue, its exchange and its dead-letter queue are
created automatically.

A `docker-compose.yml` is included in this repository if you need a local
RabbitMQ to try it against.

## Configuration

Connections are configured with a builder:

| Method | Purpose |
|---|---|
| `with_host(host: str)` | RabbitMQ broker address |
| `with_port(port: int)` | Connection port |
| `with_user(user: str)` | Username |
| `with_password(password: str)` | Password |
| `with_cluster_hosts(cluster_hosts: str)` | Connect to a multi-node cluster instance |
| `with_virtual_host(virtual_host: str)` | Target a specific virtual host |
| `with_secure_protocol(use_secure_protocol: bool)` | Use `amqps` instead of the default `amqp` |
| `build()` | Returns the configured `MessageManager` |

## Consumers

### Using the decorator

Queue only — topic and DLQ are derived automatically:

```python
@consumer_handler(queue_name="orders")
def handle_order(data):
    print(f"received: {data}")
```

Explicit queue and topic:

```python
@consumer_handler(queue_name="orders_error", topic="error_event")
def handle_error(data):
    print(f"received: {data}")
```

With a routing key:

```python
@consumer_handler(
    queue_name="orders_specific",
    topic="order_event",
    routing_key="specific_routing_key",
)
def handle_specific(data):
    print(f"received: {data}")
```

Consuming a dead-letter queue itself — disable DLQ creation so you do not get a
DLQ for your DLQ:

```python
@consumer_handler(queue_name="orders_dlq", create_dlq=False)
def handle_dlq(data):
    print(f"received: {data}")
```

### Registering manually

`ConsumerData` binds a queue, a topic and a handler:

```python
from hijiki import ConsumerData

def process_message(msg):
    print(f"received: {msg}")

consumer = ConsumerData("queue_name", "topic_name", process_message)
manager.create_consumer(consumer)
```

`ConsumerData` also accepts `queue_type` and `exchange_type` when you need to
consume from queues and exchanges that do not follow this library's defaults.

### Starting the consumers

```python
manager.start_consuming()
```

## Publishing

```python
manager.publish("orders", "message content")
```

By default the payload is published as `{"value": <content>}` to a `topic`
exchange, with no routing key and no `reply_to`. All of that is customizable:

```python
import uuid

def custom_message_mapper(topic: str, data: str):
    return {"id": str(uuid.uuid4()), "data": data}

manager.publish(
    "orders",
    "message content",
    message_mapper=custom_message_mapper,
    routing_key="my_routing_key",
    reply_to="my_response_queue",
)
```

## Using it with FastAPI

Consumers run in a separate thread so they do not block the web server, and
`is_alive()` gives you a liveness signal for health checks:

```python
import threading

threading.Thread(target=manager.start_consuming, daemon=True).start()

@app.get("/health")
def health():
    return {"messaging": manager.is_alive()}
```

## Examples

Two runnable examples live in [`examples/`](./examples):

```shell
# FastAPI: publish over HTTP, consume in a background thread
uvicorn examples.fastapi_example:app --reload

# Plain Python: publish and consume in a single script
python examples/pure_python_example.py
```

## Requirements

- A reachable RabbitMQ instance (defaults to `localhost:5672`)
- Python dependencies are installed automatically by `pip`

## Also available for

- **Node.js** → [hijiki-node](https://github.com/asengardeon/hijiki-node) ([npm](https://www.npmjs.com/package/hijiki))

## Versioning

Version 2 is a structural evolution of version 1 and keeps the public API
unchanged, so existing code migrates without adjustments. For version 1, see
[README_v1.md](README_v1.md) and the `v1_latest` tag.

## Contributing

Issues and pull requests are welcome. Open an issue to discuss larger changes
before implementing them.

## License

GPL-3.0 — see [LICENSE](LICENSE).