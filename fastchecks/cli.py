import argparse
from argparse import Namespace as NamedArgs
import asyncio
import sys
from typing import Any, Sequence

from fastchecks import conf, util, vutil, log
from fastchecks.runner import ChecksRunnerContext
from fastchecks.types import WebsiteCheck, WebsiteCheckScheduled
from fastchecks import meta

# ---------------------------------------------------------------------------

#
# Main parser
#

PARSER = argparse.ArgumentParser(
    prog=f"{meta.NAME}.cli (v{meta.VERSION})",
    description=meta.DESCRIPTION,
    epilog=f"For more help check: {meta.WEBSITE}",
)
PARSER.add_argument(
    "--pg_conninfo",
    type=vutil.validated_pg_conninfo,
    help=f"(Default: read from envar {conf._POSTGRES_CONNINFO_ENVAR_NAME}) PostgreSQL connection info in URL form (e.g. 'postgres://localhost/fastchecks')",
    default=conf._POSTGRES_CONNINFO,
)
PARSER.add_argument(
    "--pg_auto_init",
    type=vutil.validated_parsed_bool_answer,
    help="(Default: True) auto initialize the PostgreSQL database if the schema is not found",
    default=True,
)
PARSER.add_argument(
    "--log_console_level",
    choices={"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"},
    help=f"(Default: {log.DEFAULT_LOG_CONSOLE_LEVEL}) The logging level for the console",
)
PARSER.add_argument(
    "--log_root_level",
    choices={"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"},
    help="The logging level for the root logger (it affects all library loggers)",
)


# -----------------------------------------------------------------------------

#
# Common command arguments
#


def _url_kwargs(**kwargs) -> dict[str, Any]:
    return {"type": vutil.validated_web_url, "help": "The URL to check", **kwargs}


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

#
# Following subparsers (commands)
#

SUBPARSERS = PARSER.add_subparsers(
    title="Commands",
    dest="command",
    description=" ",
    help="Info:",
)

# -----------------------------------------------------------------------------


def _add_upsert_check(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "upsert_check",
        help="Write a new check to the data store, or update an existing check (uniquely identified by its URL)",
    )

    cmd.add_argument("url", **_url_kwargs())
    cmd.add_argument("--regex", **_regex_kwargs())
    cmd.add_argument("--interval", **_interval_kwargs())

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        ret = await ctx.checks.upsert(
            # The args are already validated, but just in case
            WebsiteCheckScheduled.with_check(WebsiteCheck.with_validation(x.url, x.regex), interval_seconds=x.interval)
        )
        print(ret)

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_upsert_check(SUBPARSERS)


# -----------------------------------------------------------------------------


def _add_read_all_checks(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser("read_all_checks", help="Retrieve and print all checks from the data store")

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        # AFAIK, `enumerate`, nor `itertools` can handle an async iterator, so we enumerate manually
        c = 0
        async for check in await ctx.checks.read_all():
            c += 1
            print(f"{util.str_pad(c)}: {check}")

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_read_all_checks(SUBPARSERS)


# -----------------------------------------------------------------------------


def _add_delete_check(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "delete_check",
        help="Delete a check from the data store",
    )
    cmd.add_argument("url", **_url_kwargs(help="The check's URL to delete"))

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        print(await ctx.checks.delete(x.url))

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_delete_check(SUBPARSERS)


# -----------------------------------------------------------------------------


def _add_delete_all_checks(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "delete_all_checks",
        help="Delete all checks from the data store (use with caution)",
    )
    cmd.add_argument(
        "--confirm", help="For safety, you must activate this flag to delete all checks", action="store_true"
    )

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        ret = await ctx.checks.delete_all(x.confirm)
        print("done" if ret < 0 else ret)

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_delete_all_checks(SUBPARSERS)


# -----------------------------------------------------------------------------


def _add_check_website_only(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "check_website_only",
        help="Check given single website once (without writing to the data store)",
    )
    cmd.add_argument("url", **_url_kwargs())
    cmd.add_argument("--regex", **_regex_kwargs())

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        result = await ctx.check_only(WebsiteCheck.with_validation(x.url, x.regex))
        print(result)

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_check_website_only(SUBPARSERS)


# -----------------------------------------------------------------------------


def _add_check_website(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "check_website", help="Check given single website once and write the result in the data store"
    )
    cmd.add_argument("url", **_url_kwargs())
    cmd.add_argument("--regex", **_regex_kwargs())

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        result = await ctx.check_only(WebsiteCheck.with_validation(x.url, x.regex))
        await ctx.results.write(result)
        print(result)

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_check_website(SUBPARSERS)


# -----------------------------------------------------------------------------


def _check_all_once(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "check_all_once",
        help="Check all websites once and write the results in the data store (without scheduling; you might want to schedule this command with cron)",
    )

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        c = 0
        async for check in ctx.check_all_once_n_write():
            c += 1
            print(f"{util.str_pad(c)}: {check}")

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_check_all_once(SUBPARSERS)


# -----------------------------------------------------------------------------


def _check_all_loop_fg(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    cmd = subparsers.add_parser(
        "check_all_loop_fg",
        help=f"Check all websites in the foreground at the scheduled intervals (or {conf.DEFAULT_CHECK_INTERVAL_SECONDS}s for checks without an interval)",
    )

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        await ctx.run_checks_until_stopped_in_foreground()

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_check_all_loop_fg(SUBPARSERS)


# -----------------------------------------------------------------------------


def _add_read_last_results(subparsers: argparse._SubParsersAction) -> tuple[argparse._SubParsersAction, Any]:
    _DEFAULT_READ_N_RESULTS = 10

    cmd = subparsers.add_parser("read_last_results", help="Read the last results from the data store")
    cmd.add_argument(
        "-n",
        type=vutil.validated_parsed_is_positive_int,
        help=f"(Default: {_DEFAULT_READ_N_RESULTS}) The number of results to read",
        default=_DEFAULT_READ_N_RESULTS,
    )

    async def fun(ctx: ChecksRunnerContext, x: NamedArgs):
        print("(last results first)")
        c = 0
        async for result in ctx.results.read_last_n(x.n):
            c += 1
            print(f"{util.str_pad(c)}: {result}")

    cmd.set_defaults(fun=fun)

    return (subparsers, cmd)


_add_read_last_results(SUBPARSERS)


# -----------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


def parse_validate_seq_args(argv: Sequence[str]) -> NamedArgs:
    args = PARSER.parse_args(argv)

    if args.command is None:
        print("(Error) you must specify a command\n")
        PARSER.print_help()
        sys.exit(2)

    if args.pg_conninfo is None:
        print("(Error) you must specify a PostgreSQL connection string\n")
        PARSER.print_help()
        sys.exit(2)

    return args


def parse_sys_args() -> NamedArgs:
    # ignore the first argument, which is the program name/path
    return parse_validate_seq_args(sys.argv[1:])


def parse_str_args(argv: str) -> NamedArgs:
    return parse_validate_seq_args(argv.split())


# ---------------------------------------------------------------------------


async def _run_with_namespace(args: NamedArgs) -> None:
    """Given args must and are ASSUMED to be validated"""

    if args.log_console_level is not None:
        log.reset_main_console_logger(level=args.log_console_level)
    elif args.command in ("check_website_only", "check_website", "check_all_once"):
        # Increase the level for these commands by default, because they already print the results
        log.reset_main_console_logger(level="WARNING")

    if args.log_root_level is not None:
        log.reset_root_logger(level=args.log_root_level)

    async with await ChecksRunnerContext.with_single_datastore_postgres(
        pg_conninfo=args.pg_conninfo, auto_init=args.pg_auto_init
    ) as ctx:
        await args.fun(ctx, args)


async def run_str(command: str) -> None:
    """Convenience method to run a string command"""
    args = parse_str_args(command)
    await _run_with_namespace(args)


# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_sys_args()

    try:
        asyncio.run(_run_with_namespace(args))
    except KeyboardInterrupt:
        # ignore program-exit-like exceptions in the cli
        pass


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
