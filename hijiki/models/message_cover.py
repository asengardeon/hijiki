from __future__ import annotations
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MessageCover(BaseModel):
    version: str = Field(..., description="A versão da mensagem. Ex: 'v1'.")
    value: Dict[str, Any] = Field(..., description="O objeto JSON com o payload real da mensagem.")
    context: Optional[str] = Field(None, description="Um identificador de contexto opcional.")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Um objeto com informações extras que não fazem parte do valor principal.")
