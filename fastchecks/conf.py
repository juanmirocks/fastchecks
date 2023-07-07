import os
from typing import Callable, TypeVar


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


def read_envar_value(
    envar_name: str, envar_value: _CONVERSION_OUTPUT | None, raise_error_if_none: bool = True
) -> _CONVERSION_OUTPUT:
    """
    Read cached value of the given environment variable, or, optionally, raise ValueError if the environment variable is not set.
    """
    if envar_value is None:
        raise ValueError(f"Environment variable is not set: {envar_name}")
    else:
        return envar_value


# -----------------------------------------------------------------------------


DEFAULT_REQ_TIMEOUT_SECONDS = get_typed_envar(
    "FC_DEFAULT_REQ_TIMEOUT_SECONDS", default=10.0, conversion=lambda x: float(x)
)


_POSTGRES_CONNINFO = os.environ.get("FC_POSTGRES_CONNINFO")


def get_postgres_conninfo() -> str:
    """
    Return the Postgres local connection string, or raise ValueError if the environment variable is not set.
    """
    return read_envar_value("_POSTGRES_CONNINFO", _POSTGRES_CONNINFO, raise_error_if_none=True)
