from fastchecks.log import MAIN_LOGGER as logging
from importlib import resources
from typing import AsyncIterator

from psycopg import sql
from psycopg.rows import namedtuple_row
from psycopg_pool import AsyncConnectionPool
from pydantic import PositiveInt

from fastchecks.sockets import CheckResultSocket, WebsiteCheckSocket
from fastchecks.sockets.postgres import schema
from fastchecks.types import CheckResult, WebsiteCheck, WebsiteCheckScheduled


async def common_single_pg_datastore_is_ready(pool: AsyncConnectionPool, timeout: float) -> bool:
    async with pool.connection(timeout=timeout) as aconn:
        # We just test the WebsiteCheck (written in lowercase) for existence.
        # Note: not 100% reliable (as no other objects are tested) but good enough for now.
        # MAYBE: support versioning of schemas with a hidden Version/Evolutions table or similar.
        cur = await aconn.execute(
            """
            SELECT
            FROM
                pg_tables
            WHERE
                schemaname = 'public'
                AND tablename = 'websitecheck';
                """
        )

        return cur.rowcount == 1


async def common_single_pg_datastore_init(pool: AsyncConnectionPool, timeout: float) -> bool:
    # WARNING: Assumed to not be initialized
    async with pool.connection(timeout=timeout) as aconn:
        init_sql = resources.files(schema).joinpath("up.sql").read_text()
        await aconn.execute(init_sql)
        return True


class WebsiteCheckSocketPostgres(WebsiteCheckSocket):
    def __init__(self, conninfo: str) -> None:
        self._pool = AsyncConnectionPool(conninfo)

    def is_closed(self) -> bool:
        return self._pool.closed

    async def upsert(self, check: WebsiteCheckScheduled) -> int:
        async with self._pool.connection() as aconn:
            cur = await aconn.execute(
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
            return cur.rowcount

    async def read_n(self, n: PositiveInt) -> AsyncIterator[WebsiteCheckScheduled]:
        async with self._pool.connection() as aconn:
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
        async with self._pool.connection() as aconn:
            cur = await aconn.execute(
                """
            DELETE FROM WebsiteCheck
            WHERE url = %s;""",
                (url,),
            )
            return cur.rowcount

    async def delete_all(self, confirm: bool) -> int:
        if confirm:
            async with self._pool.connection() as aconn:
                cur = await aconn.execute(
                    """
                TRUNCATE WebsiteCheck;"""
                )
                return cur.rowcount
        else:
            logging.warning("Not deleting all checks because confirm is False.")
            return 0

    async def close(self) -> None:
        return await self._pool.close()


class CheckResultSocketPostgres(CheckResultSocket):
    def __init__(self, conninfo: str) -> None:
        self._pool = AsyncConnectionPool(conninfo)

    def is_closed(self) -> bool:
        return self._pool.closed

    async def write(self, result: CheckResult) -> int:
        async with self._pool.connection() as aconn:
            cur = await aconn.execute(
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
            return cur.rowcount

    async def read_last_n(self, n: PositiveInt) -> AsyncIterator[CheckResult]:
        async with self._pool.connection() as aconn:
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
        return await self._pool.close()
