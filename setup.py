from setuptools import setup, find_packages

setup(
    name="hijiki",
    version="0.1.9",
    description="Python Rabbit wrapper library to simplify to use Exchanges and Queues with decorators",
    author="Leandro Vilson Battisti",
    keywords=['Celery', 'Kombu', 'RabbitMQ', 'decorator'],
    packages=find_packages(),
)