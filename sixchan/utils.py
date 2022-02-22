import hashlib
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Deque
from typing import Generic
from typing import Hashable
from typing import Literal
from typing import TypeVar
from typing import Union
from typing import overload

import shortuuid

T = TypeVar("T")


def get_hash_from_words(*words: str) -> str:
    digest = hashlib.md5("".join(words).encode()).digest()
    return shortuuid.encode(uuid.UUID(bytes=digest))


def paginate(page: int, pages: int, delta: int = 2, with_edge_conidtion: bool = False):
    que: Deque[int] = deque()
    que.append(page)
    for i in range(1, delta + 1):
        right = page + i
        if right <= pages:
            que.append(right)
        left = page - i
        if left >= 1:
            que.appendleft(left)

    if que[0] != 1:
        que.appendleft(1)
    if que[-1] != pages:
        que.append(pages)

    pagination: list[int | Literal["dot"]] = []
    prev = 0

    while que:
        next = que.popleft()
        if next - prev != 1:
            pagination.append("dot")
        pagination.append(next)
        prev = next

    if with_edge_conidtion:
        edge_condition = None
        if with_edge_conidtion:
            if pages == 1:
                edge_condition = (False, False)
            elif page == 1:
                edge_condition = (False, True)
            elif page == pages:
                edge_condition = (True, False)
            else:
                edge_condition = (True, True)
        return pagination, edge_condition
    else:
        return pagination


@overload
def group_by(objs: list[T], key: str, as_list: Literal[True]) -> list[list[T]]:
    ...


@overload
def group_by(
    objs: list[T], key: str, as_list: Literal[False]
) -> dict[Hashable, list[T]]:
    ...


def group_by(
    objs: list[T], key: str, as_list: bool = False
) -> Union[dict[Hashable, list[T]], list[list[T]]]:
    ids = set([getattr(obj, key) for obj in objs])
    if as_list:
        return [[obj for obj in objs if getattr(obj, key) == id_] for id_ in ids]
    return {id_: [obj for obj in objs if getattr(obj, key) == id_] for id_ in ids}


class Pagination:
    @dataclass
    class PaginationQueryModel(Generic[T]):
        page: int
        pages: int
        items: list[T]

    def __init__(self, page: int, per_page: int, total: int = None) -> None:
        self.page = page
        self.per_page = per_page
        self.total = total
        self.validate()

    def validate(self) -> None:
        if self.page < 1 or not isinstance(self.page, int):
            msg = f"page must be integer greater than or equal to 1, page:{self.page}"
            raise ValueError(msg)
        if self.per_page < 1 or not isinstance(self.per_page, int):
            msg = (
                "per_page must be integer greater than or equal to 1, "
                f"per_page:{self.per_page}"
            )
            raise ValueError(msg)

    @property
    def pages(self) -> int:
        if self.total is None:
            raise ValueError("total is None")
        return self.total // self.per_page + 1

    @property
    def limit(self) -> int:
        return self.per_page

    @property
    def offset(self) -> int:
        return self.per_page * (self.page - 1)

    def get_query_model(self, items: list[T]) -> PaginationQueryModel[T]:
        return self.PaginationQueryModel(self.page, self.pages, items)

    def get_empty_query_model(self) -> PaginationQueryModel[None]:
        return self.PaginationQueryModel(1, 1, [])
