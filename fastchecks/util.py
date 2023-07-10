import datetime
from typing import AsyncIterator, TypeVar
from urllib.parse import urlparse, urlunparse
import sys
import ctypes

import aiohttp


PRACTICAL_MAX_INT = sys.maxsize // ctypes.sizeof(ctypes.c_void_p)
"""
A practical maximum value for an integer in Python.
It's handy, for instance, to use it when you want to read all the results from a socket.

Value:
* 32bit machine: (2**31 - 1)//4 = 1152921504606846975
* 64bit machine: (2**63 - 1)//8 = 1152921504606846975

See:
https://docs.python.org/2/library/sys.html#sys.maxsize
https://stackoverflow.com/questions/855191/how-big-can-a-python-list-get#comment112727918_15739630
https://stackoverflow.com/a/1406210/341320
"""


def str_pad(c: int, size: int = 3) -> str:
    return str(c).zfill(size)


def shorten_str(x: str, max=100) -> str:
    if len(x) > max:
        x = x[:max] + "..."
    return x


def replace_url_last_segment(url: str, new_segment: str) -> str:
    """
    Example behavior (new_segment = "fastchecks"), urls:
    * "postgresql://localhost/postgres" -> "postgresql://localhost/fastchecks"
    * "postgresql://localhost/postgres?sslmode=require" -> "postgresql://localhost/fastchecks?sslmode=require"
    * "postgresql://username:password@localhost:5432/postgres?sslmode=require" -> "postgresql://username:password@localhost:5432/fastchecks?sslmode=require"
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")
    path_parts[-1] = new_segment
    modified_path = "/".join(path_parts)

    modified_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, modified_path, parsed_url.params, parsed_url.query, parsed_url.fragment)
    )

    return modified_url


def get_utcnow() -> datetime.datetime:
    """
    Return the current UTC timestamp in seconds.

    Use this method to make sure you are always using a timestamp with same timezone (UTC).
    """
    return datetime.datetime.utcnow()


def get_utcnow_time_difference_seconds(timestamp_start: datetime.datetime) -> float:
    """
    Return the time difference in seconds between the current UTC datetime and the input datetime.
    """
    return (get_utcnow() - timestamp_start).total_seconds()


def is_likely_text_based_body(response: aiohttp.ClientResponse) -> bool:
    """
    Return True if the response's content type is likely to be text-based (e.g. HTML, JSON, XML, etc.).

    Note: this method is not 100% reliable, but good enough for our purposes.
    """
    content_type = response.content_type.lower()
    return (
        response.charset is not None
        or content_type.startswith("text/")
        or content_type.endswith("+xml")
        or content_type.endswith("+json")
        or content_type.endswith("+xhtml")
        or content_type.endswith("+html")
    )


def is_content_length_less_than(response: aiohttp.ClientResponse, length: int, allow_none_content_length: bool) -> bool:
    content_length = response.headers.get("Content-Length")

    if content_length is None:
        return allow_none_content_length
    else:
        return int(content_length) < length


_A = TypeVar("_A")


# MAYBE #1 (2023-07-08) improve with real async mapping
async def async_itr_to_list(x: AsyncIterator[_A]) -> list[_A]:
    return [result async for result in x]
