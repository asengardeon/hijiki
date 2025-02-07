from hijiki.publisher.Publisher import Publisher
from tests.runner import Runner


class ExecutaDebugger():

    def __init__(self):
        self.runner = Runner()
        self.runner.run()
        self.pub = Publisher("localhost", "user", "pwd", 5672)


    def executar(self):
        self.pub = Publisher("localhost", "user", "pwd", 5672)
        self.pub.publish_message('erro_event', '{"value": "Esta é a mensagem"}')


if __name__ == '__main__':
    e = ExecutaDebugger()
    e.executar()