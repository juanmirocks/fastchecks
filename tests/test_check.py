import re
import aiohttp
import pytest
from website_monitor.check import check_website
from website_monitor.types import WebsiteCheck


TEST_TIMEOUT_SECONDS = 8


@pytest.mark.asyncio
async def test_check_website():
    async with aiohttp.ClientSession() as session:
        url = "https://example.org"

        regex = "Example D[a-z]+"
        result = await check_website(session, WebsiteCheck.create_with_validation(url, regex), timeout=TEST_TIMEOUT_SECONDS)

        assert result.url == url
        assert result.response_status == 200
        assert result.regex == regex
        assert result.regex_match == "Example Domain"


@pytest.mark.asyncio
async def test_check_website_with_impossible_timeout():
    async with aiohttp.ClientSession() as session:
        url = "https://example.org"

        result = await check_website(session, WebsiteCheck.create_with_validation(url), timeout=0.01)

        assert result.timeout_error is True
