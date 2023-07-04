import os
# We assume the environment variable, if any, is a valid float. Otherwise, the application will exit with an error early.
DEFAULT_REQ_TIMEOUT_SECONDS = float(os.environ.get("DEFAULT_REQ_TIMEOUT_SECONDS", "10.0"))