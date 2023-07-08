import asyncio
import pytest
import pytest_asyncio
from fastchecks.checks_runner import ChecksRunnerContext
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
async def test_dummy_1(setup_module):
    global WIP_TEST_STRING
    await asyncio.sleep(1)
    WIP_TEST_STRING = "hello"
    assert True


@pytest.mark.asyncio
async def test_dummy_2(setup_module):
    assert WIP_TEST_STRING == "hello"
