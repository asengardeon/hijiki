# HIJIKI
## Biblioteca de Gerenciamento de Mensagens com RabbitMQ

Este projeto fornece uma abstração para facilitar o uso do RabbitMQ em aplicações Python, incluindo suporte para FastAPI e uso puro em Python.

## 📌 Requisitos

- Python 3.7+
- RabbitMQ
- Dependências do projeto:
  ```sh
  pip install pika fastapi uvicorn
  
##  📦 Instalação
Clone este repositório e instale as dependências:

``` shell
git clone https://github.com/seu-repositorio/rabbitmq-manager.git
cd rabbitmq-manager
pip install -r requirements.txt
```

## 🚀 Como Usar
1. Exemplo com FastAPI

Inicie um servidor FastAPI para enviar mensagens ao RabbitMQ:

``` python
from fastapi import FastAPI
from message_manager import MessageManagerBuilder

app = FastAPI()

builder = MessageManagerBuilder()
manager = builder.with_host("localhost").with_port(5672).with_user("user").with_password("pwd").build()

@app.get("/publish/{queue}/{message}")
async def publish_message(queue: str, message: str):
    manager.publish(queue, message)
    return {"message": f"Message sent to {queue}"}

@app.get("/ping")
async def ping():
    return {"status": "RabbitMQ is connected" if manager.connection.ping() else "RabbitMQ is not connected"}

```

Para rodar a API:

```bash
uvicorn main:app --reload
```
## Exemplo Puro em Python

``` python
import time
from message_manager import MessageManagerBuilder

builder = MessageManagerBuilder()
manager = builder.with_host("localhost").with_port(5672).with_user("user").with_password("pwd").build()

queue = "example_queue"
message = "Hello, RabbitMQ!"

manager.publish(queue, message)
print(f"Message '{message}' sent to queue '{queue}'")

time.sleep(2)

print("Consuming messages...")

@MessageManager.rabbitmq_consumer(queue, "example_topic")
def process_message(msg):
    print(f"Received: {msg}")
```

##  🔧 Configuração com MessageManagerBuilder

O MessageManagerBuilder permite configurar a conexão com o RabbitMQ de forma flexível:

``` python
builder = MessageManagerBuilder()
manager = (builder.with_host("localhost")
                .with_port(5672)
                .with_user("user")
                .with_password("pwd")
                .with_heartbeat(60)
                .with_cluster_hosts("host1,host2")
                .build())

```
##  Métodos disponíveis no Builder:

- with_host(host: str): Define o host do RabbitMQ.  
- with_port(port: int): Define a porta do RabbitMQ.  
- with_user(user: str): Define o usuário de autenticação.  
- with_password(password: str): Define a senha de autenticação.  
- with_heartbeat(heartbeat: int): Define o tempo de heartbeat.  
- with_cluster_hosts(cluster_hosts: str): Define múltiplos hosts para conexão em cluster.  

## 📝 Licença

Esse projeto está sob a licença MIT.

---

## 🤝 Contribuição

Pull requests são bem-vindos! Para maiores detalhes leia as guidelines no [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📫 Contato

Em caso de dúvidas, abra uma issue ou envie um e-mail para: [seu@email.com]

---