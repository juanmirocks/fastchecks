-- Drop all objects in the public schema
-- Use for testing and experimenting only
-- Ref: https://stackoverflow.com/questions/3327312/how-can-i-drop-all-the-tables-in-a-postgresql-database
--
-- Likely better alternative: just drop the database and recreate it, e.g. on the CLI (and being in the fastchecks root folder):
-- _dbname="fastchecks"; dropdb "${_dbname}"; createdb "${_dbname}"; cat 'fastchecks/sockets/postgres/schema/up.sql' | psql "${_dbname}"; psql "${_dbname}" -c "\dt;"

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
