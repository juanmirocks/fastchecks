import asyncio
import sys
from fastchecks import conf, require
from fastchecks.runner import ChecksRunnerContext
from fastchecks.types import WebsiteCheck, WebsiteCheckScheduled


class __ResultsParams:
    READ_MAX_RESULTS = 100
    # To pattern match a variable's value (below), we need to use a class/enum; see: https://peps.python.org/pep-0636/#matching-against-constants-and-enums
    READ_MAX_RESULTS_OPR = f"read_last_{READ_MAX_RESULTS}_results"


async def main() -> None:
    require(len(sys.argv) in (3, 4), "Usage: python -m fastchecks.cli <opr> <url> [regex]")

    opr = sys.argv[1]
    url = sys.argv[2]
    regex_str_opt = sys.argv[3] if len(sys.argv) == 4 else None

    ctx = ChecksRunnerContext.init_with_postgres(conf.get_postgres_conninfo())

    async with ctx:
        match opr:
            case "upsert_check":
                await ctx.checks.upsert(
                    WebsiteCheckScheduled.with_check(
                        WebsiteCheck.with_validation(url, regex_str_opt), interval_seconds=None
                    )
                )

            case "read_all_checks":
                await ctx.checks.read_all()

            case "delete_check":
                await ctx.checks.delete(url)

            ###

            case "check_website_only":
                await ctx.check_only(WebsiteCheck.with_validation(url, regex_str_opt))

            case "check_website_and_write":
                result = await ctx.check_only(WebsiteCheck.with_validation(url, regex_str_opt))
                await ctx.results.write(result)

            case "check_once_all_websites_and_write":
                await ctx.check_once_all_websites_n_write()

            case __ResultsParams.READ_MAX_RESULTS_OPR:
                await ctx.results.read_last_n(__ResultsParams.READ_MAX_RESULTS)

            case _:
                raise ValueError(f"Unknown opr: {opr}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # ignore program-exit-like exceptions in the cli
        pass
