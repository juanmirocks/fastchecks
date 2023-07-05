from typing import AsyncIterator
from website_monitor.types import CheckResult
from website_monitor.sockets import CheckResultSocket
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import namedtuple_row


class CheckResultSocketPostgres(CheckResultSocket):
    __pool: AsyncConnectionPool

    @classmethod
    async def create(cls, conninfo: str) -> "CheckResultSocket":
        self = cls()
        self.__pool = AsyncConnectionPool(conninfo)
        return self

    async def write(self, result: CheckResult) -> None:
        async with self.__pool.connection() as aconn:
            await aconn.execute(
                """
            INSERT INTO CheckResult
            (url, timestamp_start, response_time, response_status, regex, regex_match, timeout_error)
            VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                (
                    result.url,
                    result.timestamp_start,
                    result.response_time,
                    result.response_status,
                    result.regex,
                    result.regex_match,
                    result.timeout_error,
                ),
            )

    async def read_all(self) -> AsyncIterator[CheckResult]:
        async with self.__pool.connection() as aconn:
            acur = await aconn.execute("""SELECT * FROM CheckResult ORDER BY timestamp_start DESC;""")
            acur.row_factory = namedtuple_row
            async for row in acur:
                yield CheckResult(
                    url=row.url,
                    timestamp_start=row.timestamp_start,
                    response_time=row.response_time,
                    response_status=row.response_status,
                    regex=row.regex,
                    regex_match=row.regex_match,
                )

    async def close(self) -> None:
        return await self.__pool.close()
