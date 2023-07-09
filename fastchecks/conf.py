import os
from typing import Callable, TypeVar
from fastchecks import require


_CONVERSION_OUTPUT = TypeVar("_CONVERSION_OUTPUT")


def get_typed_envar(
    envar_name: str, default: _CONVERSION_OUTPUT, conversion: Callable[[str], _CONVERSION_OUTPUT]
) -> _CONVERSION_OUTPUT:
    """
    Return the value of the given environment variable, or the default value if the environment variable is not set.
    """
    value = os.environ.get(envar_name)
    if value is None:
        return default
    else:
        return conversion(value)


def read_envar_value(envar_name: str, envar_value: _CONVERSION_OUTPUT | None) -> _CONVERSION_OUTPUT:
    """
    Read cached value of the given environment variable, or raise ValueError if the environment variable is not set.
    """
    if envar_value is None:
        raise ValueError(f"Environment variable is not set: {envar_name}")
    else:
        return envar_value


# -----------------------------------------------------------------------------


DEFAULT_REQ_TIMEOUT_SECONDS: float = get_typed_envar(
    "FC_DEFAULT_REQ_TIMEOUT_SECONDS", default=10.0, conversion=lambda x: float(x)
)

MIN_INTERVAL_SECONDS: int = get_typed_envar("FC_MIN_INTERVAL_SECONDS", default=5, conversion=lambda x: int(x))

MAX_INTERVAL_SECONDS: int = get_typed_envar("FC_MAX_INTERVAL_SECONDS", default=300, conversion=lambda x: int(x))

DEFAULT_CHECK_INTERVAL_SECONDS: int = get_typed_envar("FC_DEFAULT_CHECK_INTERVAL_SECONDS", default=180, conversion=lambda x: int(x))
require(
    MIN_INTERVAL_SECONDS <= DEFAULT_CHECK_INTERVAL_SECONDS <= MAX_INTERVAL_SECONDS,
    f"Interval {DEFAULT_CHECK_INTERVAL_SECONDS} must be between min ({MIN_INTERVAL_SECONDS}) and max ({MAX_INTERVAL_SECONDS})",
)

def validate_interval(interval_seconds: int) -> bool:
    return MIN_INTERVAL_SECONDS <= interval_seconds <= MAX_INTERVAL_SECONDS

# -----------------------------------------------------------------------------

TOO_BIG_CONTENT_LENGTH_KB = get_typed_envar("FC_TOO_BIG_CONTENT_LENGTH_KB", default=100000, conversion=lambda x: int(x))
"""
Limit value (in _kilo_ bytes, not kibi bytes) to consider a response's content length as too big to be read in memory.

For reference, the size of https://python.org is, as of 2023-07-06, 49943 bytes.
"""

# -----------------------------------------------------------------------------

_POSTGRES_CONNINFO: str | None = os.environ.get("FC_POSTGRES_CONNINFO")


def get_postgres_conninfo() -> str:
    """
    Return the Postgres local connection string, or raise ValueError if the environment variable is not set.
    """
    return read_envar_value("_POSTGRES_CONNINFO", _POSTGRES_CONNINFO)
