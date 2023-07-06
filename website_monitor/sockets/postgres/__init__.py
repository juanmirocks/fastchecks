from typing import AsyncIterator

from pydantic import PositiveInt
from website_monitor.types import CheckResult, WebsiteCheck
from website_monitor.sockets import CheckResultSocket, WebsiteCheckSocket
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import namedtuple_row
from psycopg import sql


class WebsiteCheckSocketPostgres(WebsiteCheckSocket):
    __pool: AsyncConnectionPool

    @classmethod
    async def create(cls, conninfo: str) -> "WebsiteCheckSocket":
        self = cls()
        self.__pool = AsyncConnectionPool(conninfo)
        return self

    async def upsert(self, check: WebsiteCheck) -> None:
        async with self.__pool.connection() as aconn:
            await aconn.execute(
                """
            INSERT INTO WebsiteCheck
            (url, regex)
            VALUES (%s, %s)
            ON CONFLICT (url) DO UPDATE
                SET regex = EXCLUDED.regex;
            """,
                (check.url, check.regex),
            )

    async def read_last_n(self, n: PositiveInt):
        async with self.__pool.connection() as aconn:
            acur = await aconn.execute(
                sql.SQL(
                    """
                SELECT * FROM WebsiteCheck
                ORDER BY id DESC
                LIMIT {};""".format(
                        n
                    )
                )
            )

            acur.row_factory = namedtuple_row
            async for row in acur:
                yield WebsiteCheck.create_without_validation(row.url, row.regex)

    async def close(self) -> None:
        return await self.__pool.close()


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
            (url, regex, timestamp_start, response_time, timeout_error, host_error, other_error, response_status, regex_match)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                (
                    result.check.url,
                    result.check.regex,
                    #
                    result.timestamp_start,
                    result.response_time,
                    #
                    result.timeout_error,
                    result.host_error,
                    result.other_error,
                    #
                    result.response_status,
                    result.regex_match,
                ),
            )

    async def read_last_n(self, n: PositiveInt):
        async with self.__pool.connection() as aconn:
            acur = await aconn.execute(
                sql.SQL(
                    """
                SELECT * FROM CheckResult
                ORDER BY timestamp_start DESC
                LIMIT {};""".format(
                        n
                    )
                )
            )

            acur.row_factory = namedtuple_row
            async for row in acur:
                yield CheckResult(
                    check=WebsiteCheck.create_without_validation(row.url, row.regex),
                    #
                    timestamp_start=row.timestamp_start,
                    response_time=row.response_time,
                    #
                    timeout_error=row.timeout_error,
                    host_error=row.host_error,
                    other_error=row.other_error,
                    #
                    response_status=row.response_status,
                    regex_match=row.regex_match,
                )

    async def close(self) -> None:
        return await self.__pool.close()
