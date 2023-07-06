import asyncio
from typing import NamedTuple
import aiohttp
import sys

from website_monitor.check import check_website
from website_monitor.sockets import CheckResultSocket, WebsiteCheckSocket
from website_monitor.sockets.postgres import CheckResultSocketPostgres, WebsiteCheckSocketPostgres
from website_monitor import conf
from website_monitor.types import CheckResult, WebsiteCheck

# -----------------------------------------------------------------------------


class Context(NamedTuple):
    session: aiohttp.ClientSession
    # Potentially we could have different backends for checks and results (e.g. Redis for checks, Postgres for results).
    checks_socket: WebsiteCheckSocket
    results_socket: CheckResultSocket

    async def __aenter__(self) -> "Context":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await asyncio.gather(self.session.close(), self.results_socket.close())


# -----------------------------------------------------------------------------


async def upsert_check(ctx: Context, check: WebsiteCheck) -> None:
    await ctx.checks_socket.upsert(check)


async def read_all_checks(ctx: Context) -> None:
    async for check in ctx.checks_socket.read_last_n(util.PRACTICAL_MAX_INT):
        print(check)


# -----------------------------------------------------------------------------


class __ResultsParams:
    READ_MAX_RESULTS = 100
    # To pattern match a variable's value (below), we need to use a class/enum; see: https://peps.python.org/pep-0636/#matching-against-constants-and-enums
    READ_MAX_RESULTS_OPR = f"read_last_{READ_MAX_RESULTS}_results"


async def check_website_only(ctx: Context, check: WebsiteCheck) -> CheckResult:
    ret = await check_website(ctx.session, check)
    print(ret)
    return ret


async def write_result(ctx: Context, result: CheckResult) -> None:
    await ctx.results_socket.write(result)


async def read_last_100_results(ctx: Context) -> None:
    async for result in ctx.results_socket.read_last_n(100):
        print(result)


# -----------------------------------------------------------------------------


async def main() -> None:
    assert len(sys.argv) in (3, 4), "Usage: python -m website_monitor.check_quick <opr> <url> [regex]"

    opr = sys.argv[1]
    url = sys.argv[2]
    regex_str_opt = sys.argv[3] if len(sys.argv) == 4 else None

    ctx = Context(
        session=aiohttp.ClientSession(),
        checks_socket=await WebsiteCheckSocketPostgres.create(conf.get_postgres_conninfo()),
        results_socket=await CheckResultSocketPostgres.create(conf.get_postgres_conninfo()),
    )

    async with ctx:
        match opr:
            case "upsert_check":
                await upsert_check(ctx, WebsiteCheck.create_with_validation(url, regex_str_opt))

            case "read_all_checks":
                await read_all_checks(ctx)

            case "check_website_only":
                await check_website_only(ctx, WebsiteCheck.create_with_validation(url, regex_str_opt))

            case "check_website_and_write":
                result = await check_website_only(ctx, WebsiteCheck.create_with_validation(url, regex_str_opt))
                await write_result(ctx, result)

            case "read_last_100_results":
                await read_last_100_results(ctx)

            case _:
                raise ValueError(f"Unknown opr: {opr}")


if __name__ == "__main__":
    asyncio.run(main())
