# 🚥 Fast website monitoring backend service

[![Pypy latest version](https://img.shields.io/pypi/v/fastchecks.svg?color=blue)](https://pypi.org/project/fastchecks/)
[![test & lint](https://github.com/juanmirocks/fastchecks/actions/workflows/test_n_lint.yml/badge.svg)](https://github.com/juanmirocks/fastchecks/actions/workflows/test_n_lint.yml)
[![Coverage Status](https://coveralls.io/repos/github/juanmirocks/fastchecks/badge.svg?branch=develop)](https://coveralls.io/github/juanmirocks/fastchecks?branch=develop)
[![Snyk](https://img.shields.io/badge/%20Snyk_security-monitored-8742B8?logo=snyk&logoColor=white)](https://github.com/juanmirocks/fastchecks/actions)


# Features

**🍀 Feature-rich**
* Websites to check & their results are stored in postgres by default 🐘 (the library is ready for other data stores / sockets).
  * You can use postgres locally installed, running on docker, or with a DBaaS, e.g. Aiven.
* Run stored all websites once, at configurable-scheduled intervals, or even with your system's cron.
* The scheduling keeps running even if the computer goes to sleep!
* CLI API (with `argparse`) & Python's (Python >= 3.11).
  * [A webserver is planned](https://github.com/juanmirocks/fastchecks/issues/3)
* ...and more!


**🚀 Speed**
* All operations are asynchronous. This app sits on 3 giants:
  * aiohttp
  * psycopg (v3)
  * APScheduler (v4)
* Written in [Python 3.11 for maximum speed](https://docs.python.org/3/whatsnew/3.11.html#summary-release-highlights) 🐍
* Speedy regex checking thanks to [google-re2 regex](https://github.com/google/re2). Note that [google-re2 syntax](https://github.com/google/re2/wiki/Syntax) is very similar to python's native `re` but not equal. In particular, backreferences are not supported, to gain on speed and [safety](https://snyk.io/blog/redos-and-catastrophic-backtracking/).
* No ORM libraries. Just good old (& safely-escaped) SQL queries.


🧘 **Safety**
* Binary or too big responses will not be read.
* Safe regex thanks to [google-re2 regex](https://github.com/google/re2).
* Security static analysis with [bandit](https://github.com/PyCQA/bandit), [snyk](https://snyk.io), and [GitHub CodeQL](https://codeql.github.com/).
* Code is fully [type-annotated](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) and type-checked with mypy.
* Further type checking with Pydantic (v2).
* Further static analysis with pyflakes.
* Safe escaping of SQL queries with [psycopg](https://www.psycopg.org/psycopg3/docs/advanced/typing.html#checking-literal-strings-in-queries).
