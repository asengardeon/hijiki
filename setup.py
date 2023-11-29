from setuptools import setup, find_packages

setup(
    name="hijiki",
    version="{{VERSION_PLACEHOLDER}}",
    description="Python Rabbit wrapper library to simplify to use Exchanges and Queues with decorators",
    author="Leandro Vilson Battisti",
    keywords=['Celery', 'Kombu', 'RabbitMQ', 'decorator'],
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "celery==5.3.4",
        "urllib3<2.0"
    ],
)
