import mne
from . import register_loader


def load_bdf(path):
    # preload=True ensures the data is loaded into memory
    raw = mne.io.read_raw_bdf(path, preload=True)
    return raw


register_loader(".bdf", load_bdf)
