"""BDF loader plugin."""

import mne

from . import register_loader

register_loader(".bdf", mne.io.read_raw_bdf)
