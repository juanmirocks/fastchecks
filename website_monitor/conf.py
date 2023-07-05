import os

# We assume the environment variable, if any, is a valid float. Otherwise, the application will exit with an error early.
DEFAULT_REQ_TIMEOUT_SECONDS = float(os.environ.get("WM_DEFAULT_REQ_TIMEOUT_SECONDS", "10.0"))

_POSTGRES_CONNINFO = os.environ.get("WM_POSTGRES_CONNINFO")


def get_postgres_conninfo() -> str:
    """
    Return the Postgres connection string.
    """
    if _POSTGRES_CONNINFO is not None:
        return _POSTGRES_CONNINFO
    else:
        raise ValueError("WM_POSTGRES_CONNINFO environment variable is not set")
