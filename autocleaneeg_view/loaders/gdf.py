"""GDF loader plugin."""

import mne

from . import register_loader

register_loader(".gdf", mne.io.read_raw_gdf)
