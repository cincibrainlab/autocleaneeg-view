"""EGI .raw and optional .mff loader plugin."""

import mne

from . import register_loader


def load_egi_raw(path):
    return mne.io.read_raw_egi(path, preload=True)


register_loader(".raw", load_egi_raw)


if hasattr(mne.io, "read_raw_mff"):  # pragma: no cover - optional dependency
    def load_mff(path):
        return mne.io.read_raw_mff(path, preload=True)

    register_loader(".mff", load_mff)
