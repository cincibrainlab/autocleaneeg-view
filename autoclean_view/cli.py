"""Compatibility wrapper for autocleaneeg_view.cli."""

from autocleaneeg_view.cli import main  # noqa: F401
from autocleaneeg_view.cli import *  # noqa: F401,F403

if __name__ == "__main__":  # pragma: no cover
    main()
