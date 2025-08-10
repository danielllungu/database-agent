from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sql-agent")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .config import settings
from .graph import build_graph

__all__ = ["settings", "build_graph", "__version__"]