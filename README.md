# 🚥 Website monitoring backend service - in Python 🐍 - check results written into PostgreSQL 🐘

[![test & lint](https://github.com/juanmirocks/fastchecks/actions/workflows/test_n_lint.yml/badge.svg)](https://github.com/juanmirocks/fastchecks/actions/workflows/test_n_lint.yml)
[![Coverage Status](https://coveralls.io/repos/github/juanmirocks/fastchecks/badge.svg?branch=develop)](https://coveralls.io/github/juanmirocks/fastchecks?branch=develop)
[![Snyk](https://img.shields.io/badge/%20Snyk_security-monitored-8742B8?logo=snyk&logoColor=white)](https://github.com/juanmirocks/fastchecks/actions)


# Features

**🚀 Speed**
* All operations are asynchronous. This app sits on 3 giants:
  * aiohttp
  * psycopg (v3)
  * APScheduler (v4)
* Speedy regex checking thanks to [google-re2 regex](https://github.com/google/re2). Note that [google-re2 syntax](https://github.com/google/re2/wiki/Syntax) is very similar to python's native `re` but not equal. In particular, backreferences are not supported, to gain on speed and [safety](https://snyk.io/blog/redos-and-catastrophic-backtracking/).
* Code is fully [type-annotated](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html).


🧘 **Safety**
* Binary or too big responses will not be read.
* Safe regex thanks to [google-re2 regex](https://github.com/google/re2).
* Security static analysis with [bandit](https://github.com/PyCQA/bandit), [snyk](https://snyk.io), and [GitHub CodeQL](https://codeql.github.com/).
* Further static analysis with mypy & pyflakes.
* Safe escaping of SQL queries with [psycopg](https://www.psycopg.org/psycopg3/docs/advanced/typing.html#checking-literal-strings-in-queries).
