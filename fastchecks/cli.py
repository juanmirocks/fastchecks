import argparse
import asyncio
import sys
from typing import Any

from fastchecks import conf, vutil
from fastchecks.runner import ChecksRunnerContext
from fastchecks.types import WebsiteCheck, WebsiteCheckScheduled
from fastchecks import meta

# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(
    prog=meta.NAME, description=meta.DESCRIPTION, epilog=f"For more help check: {meta.WEBSITE}"
)
parser.add_argument(
    "--conninfo",
    type=vutil.validated_postgres_conninfo,
    help=f"(Default: read from envar {conf._POSTGRES_CONNINFO_ENVAR_NAME}) PostgreSQL connection info",
    default=conf._POSTGRES_CONNINFO,
)
subparsers = parser.add_subparsers(title="Commands")

# -----------------------------------------------------------------------------

# Common arguments


def _url_kwargs(**kwargs) -> dict[str, Any]:
    return {"type": vutil.validated_url, "help": "The URL to check", **kwargs}


def _regex_kwargs(**kwargs) -> dict[str, Any]:
    return {
        "type": vutil.validated_regex,
        "help": "(Default: no check) The regex to match against the response body",
        **kwargs,
    }


def _interval_kwargs(**kwargs) -> dict[str, Any]:
    return {
        "type": conf.validated_parsed_interval,
        "help": f"(Default: {conf.DEFAULT_CHECK_INTERVAL_SECONDS}) The interval in _seconds_ for a check when it is scheduled to be run periodically (min: {conf.MIN_INTERVAL_SECONDS}, max: {conf.MAX_INTERVAL_SECONDS})",
        **kwargs,
    }


# -----------------------------------------------------------------------------

upsert_check = subparsers.add_parser(
    "upsert_check",
    help="Write a new check to the data store, or update an existing check (uniquely identified by its URL)",
)
upsert_check.add_argument("url", **_url_kwargs())
upsert_check.add_argument("--regex", **_regex_kwargs())
upsert_check.add_argument("--interval", **_interval_kwargs())

#

read_all_checks = subparsers.add_parser("read_all_checks", help="Retrieve and print all checks from the data store")

#

delete_check = subparsers.add_parser(
    "delete_check",
    help="Delete a check from the data store",
)
delete_check.add_argument("url", **_url_kwargs(help="The check's URL to delete"))

#

check_website_only = subparsers.add_parser(
    "check_website_only",
    help="Check a website once (without writing to the data store)",
)
check_website_only.add_argument("url", **_url_kwargs())
check_website_only.add_argument("--regex", **_regex_kwargs())

#

check_website_write = subparsers.add_parser(
    "check_website_write", help="Check a website once and write the result in the data store"
)
check_website_write.add_argument("url", **_url_kwargs())
check_website_write.add_argument("--regex", **_regex_kwargs())

#

check_once_all_websites_write = subparsers.add_parser(
    "check_once_all_websites_write", help="Check all websites once and write the results in the data store"
)

#


_DEFAULT_READ_N_RESULTS = 100

read_last_results = subparsers.add_parser("read_last_results", help="Read the last results from the data store")
read_last_results.add_argument(
    "n", type=vutil.validated_is_positive, help=f"(Default: {_DEFAULT_READ_N_RESULTS}) The number of results to read"
)


# -----------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    args = parser.parse_args(argv)
    return args


async def main() -> None:
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
    # ignore the first argument, which is the program name/path
    parse_args(sys.argv[1:])

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # ignore program-exit-like exceptions in the cli
        pass
