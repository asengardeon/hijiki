from hijiki.config.consumer_data import ConsumerData
from hijiki.manager.message_manager_builder import MessageManagerBuilder


def handle_message(msg):
    print(f"[Consumer] Recebido: {msg}")


if __name__ == "__main__":
    print("Executando o script principal...")
    # Cria o manager
    manager = (
        MessageManagerBuilder()
        .with_host("localhost")
        .with_port(5672)
        .with_user("user")
        .with_password("pwd")
        .build()
    )

    # Registra consumidor para 'python_queue'
    consumer_data = ConsumerData("python_queue", "python_topic", handle_message)
    manager.create_consumer(consumer_data)

    # Publica uma mensagem para teste
    manager.publish("python_queue", "Mensagem enviada via Python puro!")

    # Inicia o consumo de mensagens
    print("Consumindo mensagens da fila 'python_queue'... (Ctrl+C para sair)")
    try:
        manager.start_consuming()
    except KeyboardInterrupt:
        print("\nConsumo encerrado pelo usuário.")
    print("Encerrando aplicação")
