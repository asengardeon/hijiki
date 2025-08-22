from __future__ import annotations
from typing import Dict, Any, Optional
from hijiki.models.message_cover import MessageCover


class MessageBuilder:
    """
    Classe para construir objetos MessageCover de forma fluente e segura.

    Exemplo de uso:
    builder = MessageBuilder()
    capa = builder.with_version("v1").with_value({"id": 123}).build()
    """
    def __init__(self):
        # Atributos internos para armazenar os dados da mensagem.
        self._version: Optional[str] = None
        self._value: Optional[Dict[str, Any]] = None
        self._context: Optional[str] = None
        self._extra_data: Optional[Dict[str, Any]] = None

    def with_version(self, version: str) -> MessageBuilder:
        self._version = version
        return self

    def with_value(self, value: Dict[str, Any]) -> MessageBuilder:
        self._value = value
        return self

    def with_context(self, context: str) -> MessageBuilder:
        self._context = context
        return self

    def with_extra_data(self, extra_data: Dict[str, Any]) -> MessageBuilder:
        self._extra_data = extra_data
        return self

    def build(self) -> str:
        if not self._version or not self._value:
            raise ValueError("A versão e o valor da mensagem são obrigatórios e devem ser fornecidos.")

        return MessageCover(
            version=self._version,
            value=self._value,
            context=self._context,
            extra_data=self._extra_data
        ).to_json()
