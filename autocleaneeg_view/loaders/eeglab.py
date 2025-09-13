"""EEGLAB .set loader plugin."""

import mne

from . import register_loader

register_loader(".set", mne.io.read_raw_eeglab)
