-- 2048 should suffice; see: https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
CREATE DOMAIN my_url AS VARCHAR(2048);


-- 2048 should also more than suffice
CREATE domain my_pyregex AS VARCHAR(2048);


CREATE TABLE
  CheckResult (
    -- It's tempting to use the timestamp as the primary key, but the probability of collisions is not zero.
    id serial PRIMARY KEY,
    -- MAYBE If we needed to often select by website's domain, we could create a separate column for it.
    url my_url NOT NULL,
    timestamp_start TIMESTAMP NOT NULL,
    response_time REAL NOT NULL,
    response_status SMALLINT,
    regex my_pyregex,
    -- We do not store the regex match (if any); we only store if it's found or not.
    -- Several reasons: 1) save on space; 2) we don't need to really know the match; 3) we don't want to store possibly sensitive data or even extraneous data.
    regex_match BOOLEAN,
    timeout_error BOOLEAN
  );


CREATE TABLE
  WebsiteCheck (
    -- We decisively not allow duplicate URLs. If we wanted to allow multiple regex's per URL, we could use an ARRAY of regex's.
    url my_url PRIMARY KEY,
    --
    regex my_pyregex
  );
