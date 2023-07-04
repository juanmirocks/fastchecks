import re
import aiohttp
import pytest
from website_monitor.check import check_website


TEST_TIMEOUT_SECONDS = 8


@pytest.mark.asyncio
async def test_check_website():
    async with aiohttp.ClientSession() as session:
        url = "https://example.org"

        regex_str_opt = "Example D[a-z]+"
        result = await check_website(session, url, re.compile(regex_str_opt), timeout=TEST_TIMEOUT_SECONDS)

        assert result.url == url
        assert result.regex_opt == regex_str_opt
        assert result.regex_match_opt == "Example Domain"


@pytest.mark.asyncio
async def test_check_website_with_impossible_timeout():
    async with aiohttp.ClientSession() as session:
        url = "https://example.org"

        with pytest.raises(TimeoutError):
            await check_website(session, url, timeout=0.01)
