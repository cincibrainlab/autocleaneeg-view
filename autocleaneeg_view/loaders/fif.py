"""MNE .fif loader plugin."""

import mne

from . import register_loader

register_loader(".fif", mne.io.read_raw_fif)
