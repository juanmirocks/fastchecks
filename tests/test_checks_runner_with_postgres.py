import asyncio
import pytest
import pytest_asyncio
from fastchecks.checks_runner import ChecksRunnerContext
from fastchecks.types import WebsiteCheck
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
    checks00 = await async_itr_to_list(await CTX.checks.read_all())
    results00 = await async_itr_to_list(CTX.results.read_last_n(PRACTICAL_MAX_INT))

    # The DB is empty at the beginning
    assert len(checks00) == 0, f"{checks00} - {type(checks00)}"
    assert len(results00) == 0, f"{results00} - {type(results00)}"

    # We insert one check
    await CTX.checks.upsert(WebsiteCheck(url="https://python.org", regex="Python .* lets you work quickly"))
    #
    checks01 = await async_itr_to_list(await CTX.checks.read_all())
    assert len(checks01) == 1, f"{checks01} - {type(checks01)}"

    # We run & store all checks
    results02a = await async_itr_to_list(CTX.check_all_websites_and_write())
    # Another way to get the same result, just to be sure, however the result read from the DB no longer contains the matched regex text
    results02b = await async_itr_to_list(CTX.results.read_last_n(PRACTICAL_MAX_INT))
    assert len(results02a) == 1, f"{results02a} - {type(results02a)}"
    assert len(results02b) == 1, f"{results02b} - {type(results02b)}"
    assert results02a[0].is_regex_match_truthy() and results02a[0].regex_match == "Python is a programming language that lets you work quickly"
    assert results02b[0].is_regex_match_truthy() and results02b[0].regex_match == True
