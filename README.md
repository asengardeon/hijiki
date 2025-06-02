# HIJIKI - Gerenciamento de Mensagens com RabbitMQ
## 📚 Sobre a biblioteca HIJIKI

### Versão 2
Este documento descreve a biblioteca **HIJIKI** versão 2, que é uma evolução da versão 1, mantendo compatibilidade com o código existente. A versão 2 introduz melhorias significativas na estrutura e funcionalidade, mas não altera a API pública, garantindo que os usuários possam migrar facilmente sem necessidade de ajustes no código já implementado.
para acesso a versão 1, consulte a documentação da [versão 1](README_v1.md) e para fontes a tag v1_latest

HIJIKI é uma biblioteca Python de alto nível para gerenciamento de mensagens orientada a eventos, destinada a facilitar a criação, configuração e uso de consumidores e produtores de mensagens, principalmente utilizando **RabbitMQ** como broker. Seu objetivo é abstrair detalhes de implementação de fila e troca de mensagens, oferecendo uma interface intuitiva, flexível e adequada tanto para aplicações web quanto scripts standalone.

**Principais Características:**
- **Builder pattern** para configuração (`MessageManagerBuilder`), facilitando setup e customizações complexas.
- **Gerenciamento simplificado de consumidores**: registre consumidores (filas, tópicos e handlers) rapidamente usando uma API intuitiva.
- **Publicação fácil de mensagens**: uso direto de métodos para publicar em tópicos/fila, com suporte a mapeamento customizado de payloads.
- **Suporte a múltiplos brokers**: arquitetura pronta para suporte a outros brokers, embora os exemplos estejam focados em RabbitMQ.
- **Extensível**: pode ser integrada a decorators e middlewares para aplicações async/web como FastAPI ou scripts tradicionais.
- **Métodos utilitários** para manutenção do ciclo de vida do consumo, verificação de saúde (`is_alive`), troca dinâmica do broker, e registro em execução.

**Principais Classes:**
- `MessageManagerBuilder`: Classe principal para construir e configurar a stack.
- `MessageManager`: Gerencia operações de envio e consumo de mensagens.
- `ConsumerData`: Estrutura que associa uma fila, tópico e função handler.

---

##  📦 Instalação
Clone este repositório e instale as dependências:

``` shell
git clone https://github.com/asengardeon/hijiki.git
cd hijiki
pipenv  install 
```

## ⚙️ Detalhamento técnico dos métodos de uso

A seguir, um resumo técnico dos principais métodos empregados para utilizar a biblioteca HIJIKI na prática:

## 1. Criação e configuração do Manager

A configuração é feita via padrão builder, permitindo customização das conexões e parâmetros:
```
python
manager = (
    MessageManagerBuilder()
    .with_host("localhost")
    .with_port(5672)
    .with_user("user")
    .with_password("pwd")
    # outras opções, como troca do broker, etc.
    .build()
)
```
- **with_host(host: str)**: define o endereço do broker RabbitMQ.
- **with_port(port: int)**: configura a porta de conexão.
- **with_user(user: str), with_password(password: str)**: definem credenciais.
- **build()**: instancia o manager, pronto para uso.

## 2. Registro de consumidores
### Criando consumidor manualmente
É preciso criar uma instância de `ConsumerData` associando uma fila, tópico e função de processamento.  
O método **create_consumer** adiciona consumidores ao manager:
```
python
def process_message(msg):
    print(f"Mensagem recebida: {msg}")

consumer_data = ConsumerData("nome_da_fila", "nome_do_topico", process_message)
manager.create_consumer(consumer_data)
```
- O handler (função) será chamada a cada mensagem recebida nessa fila/tópico.

##Criando consumidor com decorator
Você também pode usar o decorator `@consumer_handler` para registrar consumidores de forma mais simples:

###  Modelo apenas determinando a fila
```
@consumer_handler(queue_name="teste1")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
        result_data_list.append(data)
        result_event_list.append('received event')
```
### Modelo determinando fila e que não cria fila DLQ automaticamente, aconselhado para consumidores dde filas DLQ 
```
    @consumer_handler(queue_name="teste1_dlq", create_dlq=False)
    def internal_consumer_dlq(data):
        print(f"consumiu o valor:{data}")
        result_event_list_dlq.append('received event')
```
### Modelo determinando fila e tópico
```
    @consumer_handler(queue_name="fila_erro", topic="erro_event")
    def internal_consumer_erro(data):
        print(f"consumiu o valor:{data}")
        result_event_list.append('received event')
        raise Exception("falhou")
```
### Modelos com uso de routing_key
```
    @consumer_handler(queue_name="teste_with_specific_routing_key", topic='teste1_event',
                      routing_key="specific_routing_key")
    def internal_consumer(data):
        print(f"consumiu o valor:{data}")
        result_data_list.append(data)
        result_data_list_dlq_for_specific_routing_key.append('received event')
```

## 3. Início do consumo

O método **start_consuming** inicia loops de consumo das filas para todos consumidores registrados:
```
python
manager.start_consuming()
```
- No FastAPI, recomenda-se executar em thread separada para não bloquear o servidor.

## 4. Publicação de mensagens

O método **publish** envia mensagens diretamente para a fila/ tópico definido:
```
python
manager.publish("nome_da_fila", "Conteúdo da mensagem")
```
- Mensagens podem ser publicadas a partir de endpoints FastAPI ou scripts Python, conforme exemplo.

---

## 📦 Pré-requisitos

- **RabbitMQ** rodando na máquina local (`localhost:5672`) ou disponível remotamente.
- Dependências Python instaladas:
  - `pipenv install` (na raiz do projeto)
  - Bibliotecas necessárias: `pika`, `fastapi`, `uvicorn`, entre outras já incluídas no `Pipfile` do projeto.

---

## Estrutura dos Exemplos

- [`fastapi_example.py`](./fastapi_example.py)  
  Demonstra como criar endpoints FastAPI para publicar mensagens e inicializar consumidores utilizando HIJIKI.

- [`pure_python_example.py`](./pure_python_example.py)  
  Demonstra como publicar e consumir mensagens programaticamente, usando apenas Python puro, sem framework web.

---

## ▶️ Como executar os exemplos

### 1. Exemplo FastAPI

#### **Passo a passo**

1. **Suba o RabbitMQ** em sua máquina local (padrão: usuário `user`, senha `pwd`, porta `5672`)  
   Se usar outro usuário/senha/host, edite o exemplo conforme necessário.

2. **Execute o servidor FastAPI**:
   ```sh
   uvicorn examples.fastapi_example:app --reload
   ```
3. **Interaja com a API**:
   - Publique uma mensagem:
     ```sh
     curl -X POST "http://localhost:8000/publish/fastapi_queue" -H  "accept: application/json" -d "message=Olá do FastAPI"
     ```
   - Veja os consumidores recebendo mensagens no terminal onde o servidor está rodando (mensagens são exibidas via print).

#### **Observações**
- O consumidor é registrado e inicializado automaticamente ao subir o FastAPI.
- O consumo roda em uma thread em paralelo ao servidor web.

---

### 2. Exemplo Python Puro

#### **Passo a passo**

1. **Suba o RabbitMQ** em sua máquina local (`localhost:5672`).

2. **Execute o script**:
   ```sh
   python examples/pure_python_example.py
   ```

3. **Verifique a saída**:
   - O script publica uma mensagem inicial, registra o consumidor e começa a consumir mensagens da fila `python_queue`.
   - O consumidor imprime no console todas as mensagens recebidas.

#### **Observações**
- Use `Ctrl+C` para interromper o consumo.

---

## 💡 Dicas e Customizações

- Para consumir de outras filas ou alterar tópicos, edite os nomes nos exemplos.
- Você pode registrar múltiplos consumidores, basta criar mais instâncias de `ConsumerData` e passar para `manager.create_consumer()`.
- Troque usuário, senha ou porta caso sua instância RabbitMQ seja diferente.

---

## 🛠️ Sobre a arquitetura utilizada

- Os consumidores são instâncias de `ConsumerData`, que associam fila, tópico e função de processamento.
- O método `manager.start_consuming()` inicia o consumo registrado para as filas configuradas.
- O exemplo FastAPI utiliza um thread para que o consumo de mensagens ocorra junto do serviço web.

---

## ❓ Dúvidas ou Sugestões?

Abra uma issue no repositório principal do projeto, ou envie sugestões/contribuições!

---