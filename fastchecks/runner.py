import asyncio
import logging
from typing import AsyncIterator

import aiohttp
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger

from fastchecks import conf, require, util
from fastchecks.check import check_website
from fastchecks.sockets import CheckResultSocket, WebsiteCheckSocket
from fastchecks.sockets.postgres import CheckResultSocketPostgres, WebsiteCheckSocketPostgres
from fastchecks.types import CheckResult, WebsiteCheck, WebsiteCheckScheduled

# -----------------------------------------------------------------------------


class ChecksRunnerContext:
    """
    Holds the state context to be able to run checks and store results.

    The backends/sockets for checks and results could potentially be different (e.g. Redis or even a simple text file for checks, Postgres for results).
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        checks: WebsiteCheckSocket,
        results: CheckResultSocket,
        default_interval_seconds: int | None = None,
    ) -> None:
        require(not session.closed, "Session must be open")
        require(not checks.is_closed(), "Checks socket must be open")
        require(not results.is_closed(), "Results socket must be open")

        self._aiohttp_session = session
        self.checks = checks
        self.results = results
        self.default_interval_seconds = (
            conf.DEFAULT_CHECK_INTERVAL_SECONDS
            if default_interval_seconds is None
            else conf.validate_interval(default_interval_seconds)
        )
        """Default interval for website checks that don't specify it"""

    async def __aenter__(self) -> "ChecksRunnerContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await asyncio.gather(self._aiohttp_session.close(), self.checks.close(), self.results.close())

    async def close(self) -> None:
        await self.__aexit__(None, None, None)

    # -----------------------------------------------------------------------------

    @classmethod
    def init_with_postgres(cls, postgres_conninfo: str, **kwargs) -> "ChecksRunnerContext":
        return cls(
            session=aiohttp.ClientSession(),
            checks=WebsiteCheckSocketPostgres(postgres_conninfo),
            results=CheckResultSocketPostgres(postgres_conninfo),
            **kwargs,
        )

    # -----------------------------------------------------------------------------

    async def check_only(self, check: WebsiteCheck) -> CheckResult:
        """Check website without saving into results data storage."""
        ret = await check_website(self._aiohttp_session, check)
        logging.debug(ret)
        return ret

    async def check_n_write(self, check: WebsiteCheck) -> CheckResult:
        """Check website and save into results data storage."""
        ret = await self.check_only(check)
        await self.results.write(ret)
        return ret

    async def check_once_all_websites_n_write(self) -> AsyncIterator[CheckResult]:
        async for check in self.checks.read_n(util.PRACTICAL_MAX_INT):
            result = await self.check_only(check)
            await self.results.write(result)
            yield result

    # -----------------------------------------------------------------------------

    def _get_interval_seconds(self, check: WebsiteCheckScheduled) -> int:
        return self.default_interval_seconds if check.interval_seconds is None else check.interval_seconds

    async def _add_check_to_scheduler(self, scheduler: AsyncScheduler, check: WebsiteCheckScheduled) -> AsyncScheduler:
        fun = self.check_n_write

        # Note: we can later retrieve scheduled checks by their url (with `AsyncScheduler.get_schedule``)
        # MAYBE (2023-07-09; future idea): tag the check with the url's domain, so later we can filter on them
        await scheduler.add_schedule(
            fun, trigger=IntervalTrigger(seconds=self._get_interval_seconds(check)), id=check.url, args=[check]
        )

        return scheduler

    async def _add_checks_to_scheduler(
        self, scheduler: AsyncScheduler, checks: AsyncIterator[WebsiteCheckScheduled]
    ) -> AsyncScheduler:
        async for check in checks:
            await self._add_check_to_scheduler(scheduler, check)

        return scheduler

    async def run_checks_until_stopped_in_foreground(self) -> None:
        """
        Run all saved checks until stopped (e.g. with Ctrl+C) in the foreground.
        The interval for each check is taken from the check itself, or the default interval if not specified.

        If there are no checks yet, an error is raised.
        """
        try:
            async with AsyncScheduler() as scheduler:
                async for check in await self.checks.read_all():
                    logging.info(f"Adding check to scheduler: {check}")
                    await self._add_check_to_scheduler(scheduler, check)

                require(len(await scheduler.get_schedules()) != 0, "No checks to run. Add some checks first.")

                await scheduler.run_until_stopped()

        except (KeyboardInterrupt, SystemExit):
            pass
