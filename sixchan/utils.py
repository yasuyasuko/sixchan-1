import base64
import hashlib


def get_b64encoded_digest_string_from_words(*words: list[str]) -> str:
    digest = hashlib.md5("".join(words).encode()).digest()
    return base64.b64encode(digest).decode().strip("=")
