import asyncio
import re
import aiohttp
import sys

from website_monitor.check import check_website
from website_monitor.sockets.postgres import CheckResultSocketPostgres
from website_monitor import conf


async def check_single_website_only(url: str, regex_str_opt: str | None = None) -> None:
    regex_ptr_opt = None if regex_str_opt is None else re.compile(regex_str_opt)

    async with aiohttp.ClientSession() as session:
        result = await check_website(session, url, regex_ptr_opt)
        print(result)


async def read_all_results() -> None:
    async with await CheckResultSocketPostgres.create(conf.get_postgres_conninfo()) as socket:
        async for row in socket.read_all():
            print(row)


if __name__ == "__main__":
    assert len(sys.argv) in (3, 4), "Usage: python -m website_monitor.check_quick <opr> <url> [regex]"

    opr = sys.argv[1]
    url = sys.argv[2]
    regex_str_opt = sys.argv[3] if len(sys.argv) == 4 else None

    match opr:
        case "check_single_website_only":
            asyncio.run(check_single_website_only(url, regex_str_opt))

        case "read_all_results":
            asyncio.run(read_all_results())
