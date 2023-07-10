#
# Utils for validating data values, specifically user inputs.
#

from numbers import Number

from fastchecks import meta, require


def validate_in_range(name: str, val: Number, min: Number, max: Number) -> Number:
    """
    Validate that the given value is between the given min and max, and return it if it is, otherwise raise ValueError.
    """
    require(
        min <= val <= max,
        f"{name} must be between min & max: [{min}, {max}]",
    )
    return val


def validate_postgres_conninfo(conninfo: str) -> str:
    prefix = "postgresql://"
    require(
        conninfo.startswith(prefix),
        f"The Postgres conninfo must be of URL form and start with 'postgresql://' (e.g. for a local Postgres database, 'postgresql://localhost:5432/{meta.NAME}')",
    )
    return conninfo
