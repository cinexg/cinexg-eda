from importlib.metadata import PackageNotFoundError, version

from .analyzer import analyze
from .report import report

try:
    __version__ = version("statlens")
except PackageNotFoundError:
    # Package isn't installed (e.g. running straight from a source checkout).
    __version__ = "0.0.0"

# __all__ dictates what gets imported when someone uses `from statlens import *`
__all__ = ["analyze", "report"]
