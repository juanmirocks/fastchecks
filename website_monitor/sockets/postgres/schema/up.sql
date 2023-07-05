CREATE TABLE
  CheckResult (
    -- It's tempting to use the timestamp as the primary key, but the probability of collisions is not zero.
    id serial PRIMARY KEY,
    -- 2048 should suffice; see: https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
    url VARCHAR(2048) NOT NULL,
    timestamp_start TIMESTAMP NOT NULL,
    response_time REAL NOT NULL,
    response_status SMALLINT,
    -- 2048 should also more than suffice
    regex VARCHAR(2048),
    -- We do not store the regex match (if any); we only store if it's found or not.
    -- Several reasons: 1) save on space; 2) we don't need to really know the match; 3) we don't want to store possibly sensitive data or even extraneous data.
    regex_match BOOLEAN,
    timeout_error BOOLEAN
  );
