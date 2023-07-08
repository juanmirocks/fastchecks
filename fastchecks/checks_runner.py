import asyncio
import aiohttp

from fastchecks.check import check_website
from fastchecks.sockets import CheckResultSocket, WebsiteCheckSocket
from fastchecks.sockets.postgres import CheckResultSocketPostgres, WebsiteCheckSocketPostgres
from fastchecks import require, util
from fastchecks.types import CheckResult, WebsiteCheck

# -----------------------------------------------------------------------------


class ChecksRunnerContext:
    """
    Holds the state context to be able to run checks and store results.

    The backends/sockets for checks and results could potentially be different (e.g. Redis or even a simple text file for checks, Postgres for results).
    """

    def __init__(
        self, session: aiohttp.ClientSession, checks_socket: WebsiteCheckSocket, results_socket: CheckResultSocket
    ) -> None:
        require(not session.closed, "Session must be open")
        require(not checks_socket.is_closed(), "Checks socket must be open")
        require(not results_socket.is_closed(), "Results socket must be open")

        self._session = session
        self._checks_socket = checks_socket
        self._results_socket = results_socket

    async def __aenter__(self) -> "ChecksRunnerContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await asyncio.gather(self._session.close(), self._checks_socket.close(), self._results_socket.close())

    # -----------------------------------------------------------------------------

    @classmethod
    def init_with_postgres(cls, postgres_conninfo: str) -> "ChecksRunnerContext":
        return cls(
            session=aiohttp.ClientSession(),
            checks_socket=WebsiteCheckSocketPostgres(postgres_conninfo),
            results_socket=CheckResultSocketPostgres(postgres_conninfo),
        )

    # -----------------------------------------------------------------------------

    async def upsert_check(self, check: WebsiteCheck) -> None:
        await self._checks_socket.upsert(check)

    async def read_all_checks(self) -> None:
        async for check in self._checks_socket.read_last_n(util.PRACTICAL_MAX_INT):
            print(check)

    async def delete_check(self, url: str) -> None:
        await self._checks_socket.delete(url)

    # -----------------------------------------------------------------------------

    async def check_website_only(self, check: WebsiteCheck) -> CheckResult:
        ret = await check_website(self._session, check)
        print(ret)
        return ret

    async def write_result(self, result: CheckResult) -> None:
        await self._results_socket.write(result)

    async def check_all_websites_and_write(self) -> None:
        async for check in self._checks_socket.read_last_n(util.PRACTICAL_MAX_INT):
            result = await self.check_website_only(check)
            await self.write_result(result)

    async def read_last_n_results(self, n: int) -> None:
        async for result in self._results_socket.read_last_n(n):
            print(result)
