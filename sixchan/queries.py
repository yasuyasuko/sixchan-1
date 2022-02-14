from dataclasses import dataclass
from typing import Any


@dataclass
class PaginationQueryModel:
    page: int
    pages: int
    items: list[Any]
