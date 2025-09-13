"""MNE .fif loader plugin.

Supports both Raw FIF (continuous) and Epochs FIF files.
"""

import mne

from . import register_loader


def load_fif(path):
    """Load a .fif file as Raw or Epochs.

    Tries Raw first for performance, then falls back to Epochs.
    """
    try:
        return mne.io.read_raw_fif(path, preload=True)
    except Exception:
        # Not a Raw FIF; try Epochs
        return mne.read_epochs(path, preload=True)


register_loader(".fif", load_fif)
