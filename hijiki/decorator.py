from typing import Callable


def consumer_handler(queue_name: str):
    """
    Decorator para adicionar um método como handler de uma fila.

    Args:
        queue_name (str): Nome da fila associada ao handler.

    Returns:
        Callable: A função decorada com o handler registrado.
    """

    def decorator(func: Callable):
        if not hasattr(func, 'handlers'):
            func.handlers = {}
        func.handlers[queue_name] = func  # Associa a função ao nome da fila
        return func

    return decorator