"""BrainVision .vhdr loader plugin."""

import mne

from . import register_loader


def load_vhdr(path):
    """Load BrainVision with preload for consistency."""
    return mne.io.read_raw_brainvision(path, preload=True)


register_loader(".vhdr", load_vhdr)
