from setuptools import setup, find_packages

setup(
    name="hijiki",
    version="{{VERSION_PLACEHOLDER}}",
    description="Python Rabbit wrapper library to simplify to use Exchanges and Queues with decorators",
    author="Leandro Vilson Battisti",
    keywords=['RabbitMQ', 'decorator'],
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

)
