"""Plugin registry for EEG data loaders."""

from __future__ import annotations

READERS = {}


def register_loader(extension: str, reader):
    """Register a loader for a given file extension."""
    READERS[extension.lower()] = reader


# Import built-in loader plugins so they register themselves
from . import eeglab, edf, bdf, brainvision, fif, egi, gdf, neuronexus  # noqa: F401,E402

SUPPORTED_EXTENSIONS = tuple(sorted(READERS.keys()))
