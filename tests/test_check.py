import re
import aiohttp
import pytest
from website_monitor.check import check_website


@pytest.mark.asyncio
async def test_check_website():
    async with aiohttp.ClientSession() as session:
        url = "https://example.org"

        regex_str_opt = "Example Domain"
        result = await check_website(session, url, re.compile(regex_str_opt))

        assert result.url == url
        assert result.regex_opt == regex_str_opt
        assert result.regex_match_opt == "Example Domain"
