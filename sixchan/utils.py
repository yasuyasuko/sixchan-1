import base64
import hashlib
import uuid

import shortuuid


def get_b64encoded_digest_string_from_words(*words: list[str]) -> str:
    digest = hashlib.md5("".join(words).encode()).digest()
    return base64.b64encode(digest).decode().strip("=")


def normalize_uuid_string(uuid_string: str) -> uuid.UUID:
    if len(uuid_string) == 22:
        return shortuuid.decode(uuid_string)
    else:
        return uuid.UUID(uuid_string)
