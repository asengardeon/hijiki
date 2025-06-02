from fastapi import FastAPI
from hijiki.manager.message_manager_builder import MessageManagerBuilder
from hijiki.config.consumer_data import ConsumerData

app = FastAPI()

# Inicializa o manager
manager = (
    MessageManagerBuilder()
    .with_host("localhost")
    .with_port(5672)
    .with_user("user")
    .with_password("pwd")
    .build()
)

def process_message(msg):
    print(f"[Consumer] Mensagem recebida: {msg}")

# Registra o consumidor para a fila 'fastapi_queue'
consumer_data = ConsumerData("fastapi_queue", "fastapi_topic", process_message)
manager.create_consumer(consumer_data)

# Inicia o consumo de mensagens em segundo plano ao subir o app
@app.on_event("startup")
def start_consuming():
    import threading
    thread = threading.Thread(target=manager.start_consuming, daemon=True)
    thread.start()

@app.post("/publish/{queue}")
async def publish(queue: str, message: str):
    manager.publish(queue, message)
    return {"message": f"Mensagem enviada para a fila '{queue}'"}