# Lightweight metadata only; avoid heavy imports here.
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("app")   # matches your package name if installed
except PackageNotFoundError:       # dev/editable installs or running from source
    __version__ = "0.0.0.dev"

# A package-level logger (nice for library-style code)
import logging
logger = logging.getLogger(__name__)