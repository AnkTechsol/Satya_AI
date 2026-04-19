# Stub for pagination helper
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    next_cursor: Optional[int] = None
