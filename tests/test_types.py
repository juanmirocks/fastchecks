from fastchecks.types import WebsiteCheck, WebsiteCheckScheduled


def test_WebsiteCheckScheduled():
    check = WebsiteCheck.with_validation("https://example.com", ".*")

    assert check.url == "https://example.com"
    assert check.regex == ".*"

    check_scheduled = WebsiteCheckScheduled.with_check(check, 60)

    assert check_scheduled.url == check.url == "https://example.com"
    assert check_scheduled.regex == check.regex == ".*"
    assert check_scheduled.interval_seconds == 60
