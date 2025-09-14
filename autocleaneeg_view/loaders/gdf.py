"""GDF loader plugin."""

import mne

from . import register_loader


def load_gdf(path):
    """Load GDF with preload for consistency."""
    return mne.io.read_raw_gdf(path, preload=True)


register_loader(".gdf", load_gdf)
