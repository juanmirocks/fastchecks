# 🚥 Fast website monitoring backend service

[![Pypy latest version](https://img.shields.io/pypi/v/fastchecks.svg?color=blue)](https://pypi.org/project/fastchecks/)
[![test & lint](https://github.com/juanmirocks/fastchecks/actions/workflows/test_n_lint.yml/badge.svg)](https://github.com/juanmirocks/fastchecks/actions/workflows/test_n_lint.yml)
[![Coverage Status](https://coveralls.io/repos/github/juanmirocks/fastchecks/badge.svg?branch=develop)](https://coveralls.io/github/juanmirocks/fastchecks?branch=develop)
[![Snyk](https://img.shields.io/badge/%20Snyk_security-monitored-8742B8?logo=snyk&logoColor=white)](https://github.com/juanmirocks/fastchecks/actions)



## Features

**🍀 Feature-rich**
* Websites to check & their results are stored in postgres by default 🐘 (the library is ready for other data stores / sockets).
  * You can use postgres locally installed, running on docker, or with a DBaaS, e.g. Aiven.
* Run stored all websites once, at configurable-scheduled intervals, or even with your system's cron.
* The scheduling keeps running even if the computer goes to sleep!
* Nice, configurable logging
* CLI API & Python's (Python >= 3.11).
  * A [webserver](https://github.com/juanmirocks/fastchecks/issues/3) is planned.
* ...and more!


**🚀 Speed**
* All operations are asynchronous. This app sits on 3 giants:
  * aiohttp
  * psycopg (v3)
  * APScheduler (v4)
* Written in [Python 3.11 for maximum speed](https://docs.python.org/3/whatsnew/3.11.html#summary-release-highlights) 🐍
* Speedy regex checking thanks to [google-re2 regex](https://github.com/google/re2). Note that [google-re2 syntax](https://github.com/google/re2/wiki/Syntax) is very similar to python's native `re` but not equal. In particular, backreferences are not supported, to gain on speed and [safety](https://snyk.io/blog/redos-and-catastrophic-backtracking/).
* No ORM libraries. Just good old (safely-escaped) SQL queries.


🧘 **Safety**
* Binary or too big responses will not be read.
* Safe regex thanks to [google-re2 regex](https://github.com/google/re2).
* Safe escaping of SQL queries with [psycopg](https://www.psycopg.org/psycopg3/docs/advanced/typing.html#checking-literal-strings-in-queries).
* Security static analysis with [bandit](https://github.com/PyCQA/bandit), [snyk](https://snyk.io), and [GitHub CodeQL](https://codeql.github.com/).
* Code is fully [type-annotated](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) and type-checked with mypy.
* Further type checking with Pydantic (v2).
* Further static analysis with pyflakes.



## Install

### Via pip

```shell
# You need to run this with a Python 3.11 environment -- You can manage different python versions for instance with `pyenv`
pip install -U fastchecks
```


### or via source

You need to have [python poetry](https://python-poetry.org/docs/) installed. Then:

```shell
# clone this repository
_reponame="fastchecks";
_branch="main";
git clone -b "${_branch}" "https://github.com/juanmirocks/${_reponame}";
cd ${_reponame}

# Install project
poetry install
# Enter into the project's shell environment for simplicity with the running commands
poetry shell
```


## Run

0. Create a postgres DB and take note of its postgres URL conninfo. NOTE: this app was tested with Postgres v15 only; some older versions should work too.
    * For instance, if you have a local postgres installation:
    ```shell
    _dbname="fastchecks";
    createdb "${_dbname}"

    # Its postgres URL (assuming default user) will be:
    # postgres://localhost/fastchecks

    # Then you need to pass the conninfo to the CLI,
    # * either with the explicit optional parameter `--pg_conninfo`, or
    # * by setting the envar: `FC_POSTGRES_CONNINFO`
    # For simplicity, commands below assume you've set `FC_POSTGRES_CONNINFO`, e.g.:
    export FC_POSTGRES_CONNINFO='postgres://localhost/fastchecks'
    ```

2. Add some website URLs to later check for:
    ```shell
    fastchecks upsert_check 'https://example.org'  # Add a simple URL check
    fastchecks upsert_check 'https://example.org' --regex 'Example D[a-z]+'  # Update the URL check to match the response body with a regex
    fastchecks upsert_check 'https://python.org' --interval 5  # Add another URL check with a specific interval (in seconds)
    ```

3. Run the checks at the scheduled intervals in the foreground until stopped.
    ```shell
    fastchecks check_all_loop_fg  # checks without interval will run with a default (configurable; see command help)
    ```

4. That's it! You might want to explore further options:
    * For all possibilities, run: `fastchecks -h`
    * For instance, might you want to run all checks only once (e.g. to schedule with cron), run: `fastchecks check_all_once`
    * Or run a single website check once (without registering it): `fastchecks check_website 'https://www.postgresql.org/'`



## Copyright / License

Copyright 2023 Dr. Juan Miguel Cejuela

SPDX-License-Identifier: Apache-2.0

See files: [LICENSE](./LICENSE) & [NOTICE](./NOTICE).
