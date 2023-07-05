import asyncio
import aiohttp
import sys

from website_monitor.check import check_website
from website_monitor.sockets.postgres import CheckResultSocketPostgres
from website_monitor import conf
from website_monitor.types import CheckResult, WebsiteCheck


async def check_website_only(check: WebsiteCheck) -> CheckResult:
    async with aiohttp.ClientSession() as session:
        ret = await check_website(session, check)
        print(ret)
        return ret


async def write_result(result: CheckResult) -> None:
    async with await CheckResultSocketPostgres.create(conf.get_postgres_conninfo()) as socket:
        await socket.write(result)


async def read_all_results() -> None:
    async with await CheckResultSocketPostgres.create(conf.get_postgres_conninfo()) as socket:
        async for result in socket.read_all():
            print(result)


async def main() -> None:
    assert len(sys.argv) in (3, 4), "Usage: python -m website_monitor.check_quick <opr> <url> [regex]"

    opr = sys.argv[1]
    url = sys.argv[2]
    regex_str_opt = sys.argv[3] if len(sys.argv) == 4 else None

    match opr:
        case "check_website_only":
            await check_website_only(WebsiteCheck.create_with_validation(url, regex_str_opt))

        case "check_website_and_write":
            result = await check_website_only(WebsiteCheck.create_with_validation(url, regex_str_opt))
            await write_result(result)

        case "read_all_results":
            await read_all_results()

        case _:
            raise ValueError(f"Unknown opr: {opr}")


if __name__ == "__main__":
    asyncio.run(main())
