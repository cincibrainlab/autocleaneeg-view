"""EDF loader plugin."""

import mne

from . import register_loader

register_loader(".edf", mne.io.read_raw_edf)
