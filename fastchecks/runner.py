import asyncio
from typing import AsyncIterator
import aiohttp

from fastchecks.check import check_website
from fastchecks.sockets import CheckResultSocket, WebsiteCheckSocket
from fastchecks.sockets.postgres import CheckResultSocketPostgres, WebsiteCheckSocketPostgres
from fastchecks import require, util
from fastchecks.types import CheckResult, WebsiteCheck
import logging

# -----------------------------------------------------------------------------


class ChecksRunnerContext:
    """
    Holds the state context to be able to run checks and store results.

    The backends/sockets for checks and results could potentially be different (e.g. Redis or even a simple text file for checks, Postgres for results).
    """

    def __init__(self, session: aiohttp.ClientSession, checks: WebsiteCheckSocket, results: CheckResultSocket) -> None:
        require(not session.closed, "Session must be open")
        require(not checks.is_closed(), "Checks socket must be open")
        require(not results.is_closed(), "Results socket must be open")

        self._aiohttp_session = session
        self.checks = checks
        self.results = results

    async def __aenter__(self) -> "ChecksRunnerContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await asyncio.gather(self._aiohttp_session.close(), self.checks.close(), self.results.close())

    async def close(self) -> None:
        await self.__aexit__(None, None, None)

    # -----------------------------------------------------------------------------

    @classmethod
    def init_with_postgres(cls, postgres_conninfo: str) -> "ChecksRunnerContext":
        return cls(
            session=aiohttp.ClientSession(),
            checks=WebsiteCheckSocketPostgres(postgres_conninfo),
            results=CheckResultSocketPostgres(postgres_conninfo),
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
