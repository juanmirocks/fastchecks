import asyncio
import re
import aiohttp
import sys

from website_monitor.check import check_website


async def main(url: str, regex_str_opt: str | None = None):
    regex_ptr_opt = None if regex_str_opt is None else re.compile(regex_str_opt)

    async with aiohttp.ClientSession() as session:
        result = await check_website(session, url, regex_ptr_opt)
        print(result)


if __name__ == "__main__":
    assert len(sys.argv) in (2, 3), "Usage: python -m website_monitor.check_quick_website <url> [regex]"
    # Assert number of parameters is 1, 2, or 3

    url = sys.argv[1]
    regex_str_opt = sys.argv[2] if len(sys.argv) == 3 else None

    asyncio.run(main(url, regex_str_opt))
