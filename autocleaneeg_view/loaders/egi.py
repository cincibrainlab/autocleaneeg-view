"""EGI .raw and optional .mff loader plugin."""

import mne

from . import register_loader

register_loader(".raw", mne.io.read_raw_egi)

if hasattr(mne.io, "read_raw_mff"):  # pragma: no cover - optional dependency
    register_loader(".mff", mne.io.read_raw_mff)
