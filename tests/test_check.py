import aiohttp
import pytest
from fastchecks.check import check_website
from fastchecks.types import WebsiteCheck


TEST_TIMEOUT_SECONDS = 8


@pytest.mark.asyncio
async def test_check_website():
    async with aiohttp.ClientSession() as session:
        url = "https://example.org"

        regex = "Example D[a-z]+"
        result = await check_website(
            session, WebsiteCheck.create_with_validation(url, regex), timeout=TEST_TIMEOUT_SECONDS
        )

        assert result.check.url == url
        assert result.check.regex == regex

        assert result.is_success()
        assert result.response_status == 200
        assert result.regex_match == "Example Domain"


@pytest.mark.asyncio
async def test_check_website_with_impossible_timeout():
    """
    Note: This test is not deterministic, but it's very unlikely to fail.
    For sub-second timeouts, the timeout limit is not guaranteed to be respected.
    We do the check three times, and if at least one of them times out, we consider the test as passed.
    """
    async with aiohttp.ClientSession() as session:
        url = "https://youtube.com"

        result1 = await check_website(session, WebsiteCheck.create_with_validation(url), timeout=0.01)
        result2 = await check_website(session, WebsiteCheck.create_with_validation(url), timeout=0.01)
        result3 = await check_website(session, WebsiteCheck.create_with_validation(url), timeout=0.01)

        assert (result1.timeout_error is True) or (result2.timeout_error is True) or (result3.timeout_error is True)


@pytest.mark.asyncio
async def test_check_website_with_non_existent_url():
    async with aiohttp.ClientSession() as session:
        url = "https://doesnotexistsowhathappens.xxx"

        result = await check_website(session, WebsiteCheck.create_with_validation(url), timeout=TEST_TIMEOUT_SECONDS)

        assert result.host_error is True
