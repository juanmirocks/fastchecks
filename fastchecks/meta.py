from importlib import metadata
import tomllib

_MODULE_NAME = "fastchecks"

try:
    # TODO: the file is not available when installed as a package
    with open("pyproject.toml", "rb") as f:
        _META = tomllib.load(f)

        NAME = _META["tool"]["poetry"]["name"]
        VERSION = _META["tool"]["poetry"]["version"]
        DESCRIPTION = _META["tool"]["poetry"]["description"]
        WEBSITE = _META["tool"]["poetry"].get("homepage", _META["tool"]["poetry"]["repository"])

except FileNotFoundError:
    # Back up option for now for reading the package information
    # See: https://github.com/python-poetry/poetry/issues/273
    _META = {}

    NAME = _MODULE_NAME

    try:
        VERSION = metadata.version(_MODULE_NAME)
    except:
        VERSION = ""

    DESCRIPTION = "🚥 Fast website monitoring backend service"
    WEBSITE = "https://github.com/juanmirocks/fastchecks"
