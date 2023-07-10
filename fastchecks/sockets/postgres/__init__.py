import logging
from typing import AsyncIterator
from pydantic import PositiveInt
from fastchecks.types import CheckResult, WebsiteCheckScheduled, WebsiteCheck
from fastchecks.sockets import CheckResultSocket, WebsiteCheckSocket
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import namedtuple_row
from psycopg import sql


class WebsiteCheckSocketPostgres(WebsiteCheckSocket):
    def __init__(self, conninfo: str) -> None:
        self.__pool = AsyncConnectionPool(conninfo)

    def is_closed(self) -> bool:
        return self.__pool.closed

    async def upsert(self, check: WebsiteCheckScheduled) -> None:
        async with self.__pool.connection() as aconn:
            await aconn.execute(
                """
            INSERT INTO WebsiteCheck
            (url, regex, interval_seconds)
            VALUES (%s, %s, %s)
            ON CONFLICT (url) DO UPDATE
                SET regex = EXCLUDED.regex,
                    interval_seconds = EXCLUDED.interval_seconds;
            """,
                (check.url, check.regex, check.interval_seconds),
            )

    async def read_n(self, n: PositiveInt) -> AsyncIterator[WebsiteCheckScheduled]:
        async with self.__pool.connection() as aconn:
            # We format the safe query in 2 steps (also below) to avoid false positives from bandit (B608:hardcoded_sql_expressions)
            # We follow psycopg recommendations for how to escape composed SQL queries: https://www.psycopg.org/psycopg3/docs/advanced/typing.html#checking-literal-strings-in-queries
            query_raw = """
                SELECT * FROM WebsiteCheck
                LIMIT {};"""
            query_safe = query_raw.format(n)

            acur = await aconn.execute(sql.SQL(query_safe))

            acur.row_factory = namedtuple_row
            async for row in acur:
                # without validation, because we trust the database -- its value were validated before
                yield WebsiteCheckScheduled.with_check(
                    WebsiteCheck.without_validation(row.url, row.regex), row.interval_seconds
                )

    async def delete(self, url: str) -> int:
        async with self.__pool.connection() as aconn:
            cur = await aconn.execute(
                """
            DELETE FROM WebsiteCheck
            WHERE url = %s;""",
                (url,),
            )
            return cur.rowcount

    async def delete_all(self, confirm: bool) -> int:
        if confirm:
            async with self.__pool.connection() as aconn:
                cur = await aconn.execute(
                    """
                TRUNCATE WebsiteCheck;"""
                )
                return cur.rowcount
        else:
            logging.warning("Not deleting all checks because confirm is False.")
            return 0

    async def close(self) -> None:
        return await self.__pool.close()


class CheckResultSocketPostgres(CheckResultSocket):
    def __init__(self, conninfo: str) -> None:
        self.__pool = AsyncConnectionPool(conninfo)

    def is_closed(self) -> bool:
        return self.__pool.closed

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
                    result.regex_match_to_bool_or_none(),
                ),
            )

    async def read_last_n(self, n: PositiveInt) -> AsyncIterator[CheckResult]:
        async with self.__pool.connection() as aconn:
            query_raw = """
                SELECT * FROM CheckResult
                ORDER BY timestamp_start DESC
                LIMIT {};"""
            query_safe = query_raw.format(n)

            acur = await aconn.execute(sql.SQL(query_safe))

            acur.row_factory = namedtuple_row
            async for row in acur:
                yield CheckResult(
                    check=WebsiteCheck.without_validation(row.url, row.regex),
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
