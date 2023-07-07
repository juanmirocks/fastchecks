import pytest

from website_monitor import require


def test_require_on_true():
    try:
        require(True, "xxx")
    except ValueError:
        pytest.fail("require raised ValueError unexpectedly")


def test_require_on_false():
    with pytest.raises(ValueError) as excinfo:
        require(False, "xxx")

    assert str(excinfo.value) == "requirement failed: xxx"
