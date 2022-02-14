import base64
import hashlib
from collections import deque
from typing import Hashable
from typing import Optional
from typing import TypeVar
from typing import Union

T = TypeVar("T")


def get_b64encoded_digest_string_from_words(*words: list[str]) -> str:
    digest = hashlib.md5("".join(words).encode()).digest()
    return base64.b64encode(digest).decode().strip("=")


def paginate(page: int, pages: int, delta: int = 2, with_edge_conidtion: bool = False):
    que = deque()
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

    pagination = []
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


def group_by(
    objs: list[T], key: str, as_list: Optional[bool] = False
) -> Union[dict[Hashable, T], list[T]]:
    ids = set([getattr(obj, key) for obj in objs])
    if as_list:
        return [[obj for obj in objs if getattr(obj, key) == id_] for id_ in ids]
    return {id_: [obj for obj in objs if getattr(obj, key) == id_] for id_ in ids}
