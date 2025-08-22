from __future__ import annotations
import json
from typing import Dict, Any, Optional


class MessageCover:
    def __init__(
        self,
        version: str,
        value: Dict[str, Any],
        context: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        self.version = version
        self.value = value
        self.context = context
        self.extra_data = extra_data

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "version": self.version,
            "value": self.value,
        }
        if self.context is not None:
            data["context"] = self.context
        if self.extra_data is not None:
            data["extra_data"] = self.extra_data
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
