import os
from fastchecks.util import replace_url_last_segment
from tests.tutil import gen_random_timestamped_str


TEST_POSTGRES_DEFAULT_DB_CONNINFO = os.environ.get(
    "FC_TEST_POSTGRES_DEFAULT_DB_CONNINFO", "postgresql://localhost/postgres"
)


def gen_new_random_dbname() -> str:
    return f"test_fastchecks_{gen_random_timestamped_str()}"


def gen_new_test_postgres_conninfo() -> tuple[str, str]:
    new_random_dbname = gen_new_random_dbname()
    new_random_conninfo = replace_url_last_segment(TEST_POSTGRES_DEFAULT_DB_CONNINFO, new_random_dbname)

    return (new_random_dbname, new_random_conninfo)
