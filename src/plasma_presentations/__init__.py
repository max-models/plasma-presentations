"""Talks written as Quarto slides with the max-models look: HTML with reveal.js, PDF with Beamer."""

from importlib.metadata import PackageNotFoundError, version

import scope_profiler as sp

from plasma_presentations._profiling import PROFILE_TAGS
from plasma_presentations.talk import (
    FORMATS,
    figure,
    find_quarto,
    has_extension,
    install_extension,
    new_talk,
    render,
)

try:
    __version__ = version("plasma-presentations")
except PackageNotFoundError:  # not installed, e.g. run from a source tree
    __version__ = "0.0.0+unknown"

# The decorated functions pick the tag up, so registering after the imports is in time.
sp.register_opt_in_tag(*PROFILE_TAGS)

__all__ = [
    "FORMATS",
    "__version__",
    "figure",
    "find_quarto",
    "has_extension",
    "install_extension",
    "new_talk",
    "render",
]
