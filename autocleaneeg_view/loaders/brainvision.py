"""BrainVision .vhdr loader plugin."""

import mne

from . import register_loader

register_loader(".vhdr", mne.io.read_raw_brainvision)
