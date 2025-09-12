"""Legacy alias for ``autocleaneeg_view.cli``.

This module exists for backward compatibility only. It re-exports the
``main`` entrypoint from ``autocleaneeg_view.cli`` so that imports like
``from autoclean_view.cli import main`` continue to work while all logic
is centralized in the new package.
"""

from __future__ import annotations

import warnings

# Re-export symbols from the new CLI module
from autocleaneeg_view.cli import *  # noqa: F401,F403
from autocleaneeg_view.cli import main  # noqa: F401


warnings.warn(
    "autoclean_view.cli is deprecated; use autocleaneeg_view.cli instead.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = [*globals().get("__all__", []), "main"]
