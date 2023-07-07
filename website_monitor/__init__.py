__REQUIREMENT_FAILED_MSG_SUFFIX = "requirement failed"


def require(condition: bool, message: str | None = None) -> None:
    """
    Raise ValueError if condition is False, ala scala's `require` function.

    Safe alternative to `assert` to verify value input requirements.
    Note that the statement `assert` is not executed in production by default.
    See:
    * https://bandit.readthedocs.io/en/latest/plugins/b101_assert_used.html#b101-test-for-use-of-assert
    * https://snyk.io/blog/the-dangers-of-assert-in-python/
    """
    if not condition:
        msg = __REQUIREMENT_FAILED_MSG_SUFFIX if message is None else f"{__REQUIREMENT_FAILED_MSG_SUFFIX}: {message}"
        raise ValueError(msg)
