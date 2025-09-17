"""Plugin registry for EEG data loaders."""

from __future__ import annotations

READERS = {}
SUPPORTED_EXTENSIONS = ()


def register_loader(extension: str, reader):
    """Register a loader for a given file extension."""
    READERS[extension.lower()] = reader
    global SUPPORTED_EXTENSIONS
    SUPPORTED_EXTENSIONS = tuple(sorted(READERS.keys()))


# Import built-in loader plugins so they register themselves
from . import eeglab, edf, bdf, brainvision, fif, egi, gdf, neuronexus  # noqa: F401,E402
