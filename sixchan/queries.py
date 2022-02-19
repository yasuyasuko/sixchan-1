from dataclasses import dataclass
from typing import Generic
from typing import TypeVar

T = TypeVar("T")


@dataclass
class PaginationQueryModel(Generic[T]):
    page: int
    pages: int
    items: list[T]
