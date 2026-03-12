from .analyzer import analyze
from .report import report

__version__ = "0.1.0"

# __all__ dictates what gets imported when someone uses `from cinexg_eda import *`
__all__ = ["analyze", "report"]