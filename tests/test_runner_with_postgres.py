import asyncio
import pytest
import pytest_asyncio
from fastchecks.runner import ChecksRunnerContext
from fastchecks.types import WebsiteCheckScheduled, WebsiteCheck
from fastchecks.util import PRACTICAL_MAX_INT, async_itr_to_list
from tests import tconf
from fastchecks.sockets.postgres import schema
from importlib import resources
import psycopg
from psycopg import sql
import logging


TEST_DBNAME: str
TEST_CONNINFO: str
CTX: ChecksRunnerContext


# See trick for pytest async: https://stackoverflow.com/a/56238383/341320
@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# Ref for async fixture: https://stackoverflow.com/a/74352786/341320
@pytest_asyncio.fixture(scope="module")
async def setup_module():
    ###
    ### setup
    ###
    global TEST_DBNAME, TEST_CONNINFO, CTX

    (TEST_DBNAME, TEST_CONNINFO) = tconf.gen_new_test_postgres_conninfo()
    print(f"setup & run new db: {TEST_DBNAME}")

    init_sql = resources.files(schema).joinpath("up.sql").read_text()

    # We need auto-commit mode to run the CREATE DATABASE command
    with psycopg.connect(tconf.TEST_POSTGRES_DEFAULT_DB_CONNINFO, autocommit=True) as conn:
        # Debug Postgres version
        print(conn.execute("SELECT version()").fetchone())

        query_tmpl = "CREATE DATABASE {}"
        query_safe = sql.SQL(query_tmpl).format(sql.Identifier(TEST_DBNAME))
        print(conn.execute(query_safe).statusmessage)

    # Init the SQL schema
    with psycopg.connect(TEST_CONNINFO) as conn:
        print(conn.execute(init_sql).rowcount)

    CTX = ChecksRunnerContext.init_with_postgres(TEST_CONNINFO)

    yield "initialized"

    ###
    ### teardown
    ###

    try:
        # We need to close the context (in particular the postgres sockets' pools) BEFORE dropping the test database
        # Otherwise, below we get the error "database is being accessed by other users"
        await CTX.close()
        assert CTX.checks.is_closed() and CTX.results.is_closed()
    except Exception as e:
        logging.error(f"Exception when closing the context: {e}", exc_info=True)

    try:
        # We need auto-commit mode to run the DROP DATABASE command
        print(f"teardown & drop db: {TEST_DBNAME}")
        with psycopg.connect(tconf.TEST_POSTGRES_DEFAULT_DB_CONNINFO, autocommit=True) as conn:
            # FORCE to avoid error "database is being accessed by other users"
            # This should not happen since we closed the context above, but just in case
            # We need to make sure to drop the test dabase always
            # ref: https://stackoverflow.com/a/17461681/341320
            query_tmpl = "DROP DATABASE {} WITH (FORCE)"
            query_safe = sql.SQL(query_tmpl).format(sql.Identifier(TEST_DBNAME))
            print(conn.execute(query_safe).statusmessage)
    except Exception as e:
        logging.error(f"Exception when dropping the test db ({TEST_DBNAME}): {e}", exc_info=True)


# -----------------------------------------------------------------------------

WIP_TEST_STRING: str | None = None


@pytest.mark.asyncio
async def test_simple_checks_workflow(setup_module):
    global CTX

    #
    # 01: The DB is empty at the beginning
    #
    checks00 = await async_itr_to_list(await CTX.checks.read_all())
    results00 = await async_itr_to_list(CTX.results.read_last_n(PRACTICAL_MAX_INT))
    assert len(checks00) == 0, f"{checks00} - {type(checks00)}"
    assert len(results00) == 0, f"{results00} - {type(results00)}"

    # We expect an error since there are no checks yet
    with pytest.raises(ValueError):
        await CTX.run_checks_until_stopped_in_foreground()

    #
    # 02: We insert 1 check; we expect to read back 1 check
    #
    await CTX.checks.upsert(
        WebsiteCheckScheduled.with_check(
            WebsiteCheck.with_validation(url="https://python.org", regex="Python .* lets you work quickly"),
            interval_seconds=None,
        )
    )
    #
    checks01 = await async_itr_to_list(await CTX.checks.read_all())
    assert len(checks01) == 1, f"{checks01} - {type(checks01)}"

    #
    # 03: We run & store all checks; we expect to see 1 check and 1 result
    #
    results02a = await async_itr_to_list(CTX.check_once_all_websites_n_write())
    # Another way to get the same result, just to be sure, however the result read from the DB no longer contains the matched regex text
    results02b = await async_itr_to_list(CTX.results.read_last_n(PRACTICAL_MAX_INT))
    assert len(results02a) == 1, f"{results02a} - {type(results02a)}"
    assert len(results02b) == 1, f"{results02b} - {type(results02b)}"
    assert (
        results02a[0].is_regex_match_truthy()
        and results02a[0].regex_match == "Python is a programming language that lets you work quickly"
    )
    assert results02b[0].is_regex_match_truthy() and results02b[0].regex_match == True

    #
    # 04: We insert 1 more check, and then run & store all checks; we expect to see 2 checks and 3 total results
    #
    await CTX.checks.upsert(
        WebsiteCheckScheduled.with_check(
            WebsiteCheck.with_validation(url="https://example.org", regex="Example D[a-z]+"), interval_seconds=None
        )
    )
    checks03 = await async_itr_to_list(await CTX.checks.read_all())
    results03_only_last_2_results = await async_itr_to_list(CTX.check_once_all_websites_n_write())
    results03_all_results = await async_itr_to_list(CTX.results.read_last_n(PRACTICAL_MAX_INT))
    #
    assert len(checks03) == 2, f"{checks03} - {type(checks03)}"
    assert (
        len(results03_only_last_2_results) == 2
    ), f"{results03_only_last_2_results} - {type(results03_only_last_2_results)}"
    assert len(results03_all_results) == 3, f"{results03_all_results} - {type(results03_all_results)}"

    #
    # 05: We update a past check, and then run & store all checks; we expect to see 2 checks (still) and 5 total results
    #
    await CTX.checks.upsert(
        WebsiteCheckScheduled.with_check(
            WebsiteCheck.with_validation(url="https://example.org", regex=None), interval_seconds=None
        )
    )
    checks04 = await async_itr_to_list(await CTX.checks.read_all())
    results04_only_last_2_results = await async_itr_to_list(CTX.check_once_all_websites_n_write())
    results04_all_results = await async_itr_to_list(CTX.results.read_last_n(PRACTICAL_MAX_INT))
    #
    assert len(checks04) == 2, f"{checks04} - {type(checks04)}"
    assert (
        len(results04_only_last_2_results) == 2
    ), f"{results04_only_last_2_results} - {type(results04_only_last_2_results)}"
    assert len(results04_all_results) == 5, f"{results04_all_results} - {type(results04_all_results)}"
