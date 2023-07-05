import asyncio
import aiohttp
import sys

from website_monitor.check import check_website
from website_monitor.sockets.postgres import CheckResultSocketPostgres
from website_monitor import conf
from website_monitor.types import WebsiteCheck


async def check_single_website_only(check: WebsiteCheck) -> None:
    async with aiohttp.ClientSession() as session:
        result = await check_website(session, check)
        print(result)


async def read_all_results() -> None:
    async with await CheckResultSocketPostgres.create(conf.get_postgres_conninfo()) as socket:
        async for result in socket.read_all():
            print(result)


if __name__ == "__main__":
    assert len(sys.argv) in (3, 4), "Usage: python -m website_monitor.check_quick <opr> <url> [regex]"

    opr = sys.argv[1]
    url = sys.argv[2]
    regex_str_opt = sys.argv[3] if len(sys.argv) == 4 else None

    match opr:
        case "check_single_website_only":
            asyncio.run(check_single_website_only(WebsiteCheck.create_with_validation(url, regex_str_opt)))

        case "read_all_results":
            asyncio.run(read_all_results())
