import argparse
from argparse import Namespace as NamedArgs
import asyncio
import sys
from typing import Any

from fastchecks import conf, util, vutil
from fastchecks.runner import ChecksRunnerContext
from fastchecks.types import WebsiteCheck, WebsiteCheckScheduled
from fastchecks import meta

# ---------------------------------------------------------------------------

#
# Main parser
#

parser = argparse.ArgumentParser(
    prog=meta.NAME, description=meta.DESCRIPTION, epilog=f"For more help check: {meta.WEBSITE}"
)
parser.add_argument(
    "--pg_conninfo",
    type=vutil.validated_postgres_conninfo,
    help=f"(Default: read from envar {conf._POSTGRES_CONNINFO_ENVAR_NAME}) PostgreSQL connection info",
    default=conf._POSTGRES_CONNINFO,
)
subparsers = parser.add_subparsers(
    title="Commands",
    dest="command",
    description=" ",
    help="Info:",
)

# -----------------------------------------------------------------------------

#
# Common command arguments
#


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


def _add_upsert_check(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "upsert_check",
        help="Write a new check to the data store, or update an existing check (uniquely identified by its URL)",
    )

    cmd.add_argument("url", **_url_kwargs())
    cmd.add_argument("--regex", **_regex_kwargs())
    cmd.add_argument("--interval", **_interval_kwargs())

    async def fun(x: NamedArgs):
        await x.ctx.checks.upsert(
            # The args are already validated, but just in case
            WebsiteCheckScheduled.with_check(WebsiteCheck.with_validation(x.url, x.regex), interval_seconds=x.interval)
        )

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_upsert_check(subparsers)


# -----------------------------------------------------------------------------


def _add_read_all_checks(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser("read_all_checks", help="Retrieve and print all checks from the data store")

    async def fun(x: NamedArgs):
        # AFAIK, `enumerate`, nor `itertools` can handle an async iterator, so we enumerate manually
        c = 0
        async for check in await x.ctx.checks.read_all():
            c += 1
            print(f"{util.str_pad(c)}: {check}")

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_read_all_checks(subparsers)


# -----------------------------------------------------------------------------


def _add_delete_check(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "delete_check",
        help="Delete a check from the data store",
    )
    cmd.add_argument("url", **_url_kwargs(help="The check's URL to delete"))

    async def fun(x: NamedArgs):
        await x.ctx.checks.delete(x.url)

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_delete_check(subparsers)


# -----------------------------------------------------------------------------


def _add_check_website_only(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "check_website_only",
        help="Check given single website once (without writing to the data store)",
    )
    cmd.add_argument("url", **_url_kwargs())
    cmd.add_argument("--regex", **_regex_kwargs())

    async def fun(x: NamedArgs):
        result = await x.ctx.check_only(WebsiteCheck.with_validation(x.url, x.regex))
        print(result)

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_check_website_only(subparsers)


# -----------------------------------------------------------------------------


def _add_check_website(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "check_website", help="Check given single website once and write the result in the data store"
    )
    cmd.add_argument("url", **_url_kwargs())
    cmd.add_argument("--regex", **_regex_kwargs())

    async def fun(x: NamedArgs):
        result = await x.ctx.check_only(WebsiteCheck.with_validation(x.url, x.regex))
        await x.ctx.results.write(result)
        print(result)

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_check_website(subparsers)


# -----------------------------------------------------------------------------


def _check_once_all(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "check_once_all", help="Check all websites once and write the results in the data store"
    )

    async def fun(x: NamedArgs):
        c = 0
        async for check in x.ctx.check_once_all_websites_n_write():
            c += 1
            print(f"{util.str_pad(c)}: {check}")

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_check_once_all(subparsers)


# -----------------------------------------------------------------------------


def _add_read_last_results(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    _DEFAULT_READ_N_RESULTS = 100

    cmd = subparsers.add_parser("read_last_results", help="Read the last results from the data store")
    cmd.add_argument(
        "-n",
        type=vutil.validated_parsed_is_positive_int,
        help=f"(Default: {_DEFAULT_READ_N_RESULTS}) The number of results to read",
        default=_DEFAULT_READ_N_RESULTS,
    )

    async def fun(x: NamedArgs):
        c = 0
        async for result in x.ctx.results.read_last_n(x.n):
            c += 1
            print(f"{util.str_pad(c)}: {result}")

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_read_last_results(subparsers)


# -----------------------------------------------------------------------------


def parse_str_args(argv: str) -> NamedArgs:
    return parse_args(argv.split())


def parse_args(argv: list[str]) -> NamedArgs:
    args = parser.parse_args(argv)
    return args


async def main(args: NamedArgs) -> None:
    # args must and are assumed to be validated

    async with ChecksRunnerContext.init_with_postgres(conf.get_postgres_conninfo()) as ctx:
        args.ctx = ctx

        await args.fun(args)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # ignore the first argument, which is the program name/path
    args = parse_args(sys.argv[1:])

    try:
        asyncio.run(main(args))
    except (KeyboardInterrupt, SystemExit):
        # ignore program-exit-like exceptions in the cli
        pass
