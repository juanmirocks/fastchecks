import pytest
from fastchecks import conf
from tests import tconf


def test_read_envar_value_raises_exception_if_envar_is_not_set():
    with pytest.raises(ValueError):
        conf.read_envar_value("irrelevant", None)


def test_get_postgres_conninfo_means_the_envar_is_defined_or_exception_is_raised():
    conf._POSTGRES_CONNINFO

    try:
        value = conf.get_postgres_conninfo()
        assert value == conf._POSTGRES_CONNINFO
    except ValueError:
        assert conf._POSTGRES_CONNINFO is None
