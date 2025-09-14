"""EDF loader plugin."""

import mne

from . import register_loader


def load_edf(path):
    """Load EDF with preload for consistency."""
    return mne.io.read_raw_edf(path, preload=True)


register_loader(".edf", load_edf)
