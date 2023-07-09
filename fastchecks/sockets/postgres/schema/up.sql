-- 2048 should suffice; see: https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
CREATE DOMAIN my_url AS VARCHAR(2048);


-- 2048 should also more than suffice
CREATE domain my_pyregex AS VARCHAR(2048);


CREATE TABLE
  -- WebsiteCheck (Scheduled)
  WebsiteCheck (
    -- We decisively not allow duplicate URLs. If we wanted to allow multiple regex's per URL, we could use an ARRAY of regex's.
    url my_url PRIMARY KEY,
    regex my_pyregex,
    -- Note: the maximum positive value for smallint is 32767 (seconds), meaning a maximum of ~9 hours. We expect to use intervals of a max a few minutes.
    interval_seconds SMALLINT
  );


-- It's tempting to use the timestamp as the primary key, but the probability of collisions is not zero.
-- MAYBE (future idea) If we needed to often select by website's domain, we could create a separate column for it.
-- Note: we don't cross-reference the WebsiteCheck with a key, because a result may be stored even if the website is no longer being checked (or was never stored).
CREATE TABLE
  CheckResult (
    id serial PRIMARY KEY,
    --
    --
    url my_url NOT NULL,
    regex my_pyregex,
    --
    --
    timestamp_start TIMESTAMP NOT NULL,
    response_time REAL NOT NULL,
    --
    --
    timeout_error BOOLEAN NOT NULL,
    host_error BOOLEAN NOT NULL,
    other_error BOOLEAN NOT NULL,
    --
    response_status SMALLINT,
    -- We do not store the regex match (if any); we only store if it's found or not.
    -- Several reasons: 1) save on space; 2) we likely don't need to know the match; 3) we don't want to store possibly sensitive data or even extraneous data.
    regex_match BOOLEAN
  );


-- Note: we don't set up a foreign key on the url. We might have check results for websites that were never stored or are no longer being checked.
CREATE INDEX result__url__idx ON CheckResult USING hash (url);


-- Create index on timestamp_start, descending, since we will often want to select the most recent results.
CREATE INDEX result__timestamp_start__desc__idx ON CheckResult USING btree (timestamp_start DESC);
