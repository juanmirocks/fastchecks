from typing import Iterator
from website_monitor.types import CheckResult, CheckResultSocket
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import namedtuple_row


class CheckResultSocketPostgres(CheckResultSocket):

    __pool: AsyncConnectionPool

    @classmethod
    async def create(cls, conninfo: str) -> "CheckResultSocket":
        self = cls()
        self.__pool = AsyncConnectionPool(conninfo)
        return self

    async def write(self, check_result: CheckResult) -> None:
        ...

    async def read_all(self) -> Iterator[CheckResult]:
        async with self.__pool.connection() as aconn:
            acur = await aconn.execute("SELECT * FROM CheckResult;")
            acur.row_factory = namedtuple_row
            async for row in acur:
                yield CheckResult(url=row.url, timestamp_start=row.timestamp_start, response_time=row.response_time, response_status=row.response_status, regex_opt=row.regex, regex_match_opt=row.regex_match)

    async def close(self) -> None:
        return await self.__pool.close()
