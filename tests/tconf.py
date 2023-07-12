import os
import random
import string
from fastchecks.util import replace_url_last_segment, get_utcnow


TEST_POSTGRES_DEFAULT_DB_CONNINFO = os.environ.get(
    "FC_TEST_POSTGRES_DEFAULT_DB_CONNINFO", "postgresql://localhost/postgres"
)


def gen_random_timestamped_str() -> str:
    return f"{os.urandom(8).hex()}_{int(get_utcnow().timestamp())}"


def gen_new_random_dbname() -> str:
    return f"test_fastchecks_{gen_random_timestamped_str()}"


def gen_new_test_postgres_conninfo() -> tuple[str, str]:
    new_random_dbname = gen_new_random_dbname()
    new_random_conninfo = replace_url_last_segment(TEST_POSTGRES_DEFAULT_DB_CONNINFO, new_random_dbname)

    return (new_random_dbname, new_random_conninfo)


def gen_random_str(min_len: int, max_len: int | None = None) -> str:
    """
    Generate random string of given length. If two values are given, the generated random string will have a random length between the given min & max lengths.
    """
    # Following "nosec B311" skip bandit warnings, which are not relevant for this testing purpose: https://bandit.readthedocs.io/en/1.7.5/blacklists/blacklist_calls.html?highlight=b311#b311-random)
    len = min_len if max_len is None else random.randint(min_len, max_len)  # nosec B311
    return "".join(random.choices(string.ascii_letters, k=len))  # nosec B311
