from __future__ import annotations

import json
from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SafeJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder supporting Pydantic models, Enums, sets (sorted), and datetimes.
    Guarantees deterministic output for caching and hashing.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, set | frozenset):
            return sorted(obj)
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return super().default(obj)


def serialize_json(value: Any, sort_keys: bool = False) -> str:
    """
    Serialize any data structure to a JSON string safely without pickle.
    """
    if isinstance(value, BaseModel):
        return json.dumps(value.model_dump(mode="json"), cls=SafeJSONEncoder, sort_keys=sort_keys)
    return json.dumps(value, cls=SafeJSONEncoder, sort_keys=sort_keys)


def deserialize_json(payload: str, target_cls: type[T] | None = None) -> Any:
    """
    Deserialize JSON string into native types or validate against a Pydantic model.
    """
    parsed = json.loads(payload)
    if target_cls is not None and issubclass(target_cls, BaseModel):
        return target_cls.model_validate(parsed)
    return parsed
