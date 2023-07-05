import asyncio
from typing import NamedTuple
import aiohttp
import sys

from website_monitor.check import check_website
from website_monitor.sockets.postgres import CheckResultSocketPostgres
from website_monitor import conf
from website_monitor.types import CheckResult, WebsiteCheck

# -----------------------------------------------------------------------------


class Context(NamedTuple):
    session: aiohttp.ClientSession
    socket: CheckResultSocketPostgres

    async def __aenter__(self) -> "Context":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await asyncio.gather(self.session.close(), self.socket.close())


# -----------------------------------------------------------------------------


async def check_website_only(ctx: Context, check: WebsiteCheck) -> CheckResult:
    ret = await check_website(ctx.session, check)
    print(ret)
    return ret


async def write_result(ctx: Context, result: CheckResult) -> None:
    await ctx.socket.write(result)


async def read_all_results(ctx: Context) -> None:
    async for result in ctx.socket.read_all():
        print(result)


# -----------------------------------------------------------------------------


async def main() -> None:
    assert len(sys.argv) in (3, 4), "Usage: python -m website_monitor.check_quick <opr> <url> [regex]"

    opr = sys.argv[1]
    url = sys.argv[2]
    regex_str_opt = sys.argv[3] if len(sys.argv) == 4 else None

    ctx = Context(
        session=aiohttp.ClientSession(), socket=await CheckResultSocketPostgres.create(conf.get_postgres_conninfo())
    )

    async with ctx:
        match opr:
            case "check_website_only":
                await check_website_only(ctx, WebsiteCheck.create_with_validation(url, regex_str_opt))

            case "check_website_and_write":
                result = await check_website_only(ctx, WebsiteCheck.create_with_validation(url, regex_str_opt))
                await write_result(ctx, result)

            case "read_all_results":
                await read_all_results(ctx)

            case _:
                raise ValueError(f"Unknown opr: {opr}")


if __name__ == "__main__":
    asyncio.run(main())
