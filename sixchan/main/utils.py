import uuid

import shortuuid


def normalize_uuid_string(uuid_string: str) -> uuid.UUID:
    if len(uuid_string) == 22:
        return shortuuid.decode(uuid_string)
    else:
        return uuid.UUID(uuid_string)
