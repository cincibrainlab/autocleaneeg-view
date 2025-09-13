import mne
from . import register_loader


def load_bdf(path):
    # preload=True ensures the data is loaded into memory
    raw = mne.io.read_raw_bdf(path, preload=True)
    # set a reference (otherwise BioSemi looks flat)
    raw.set_eeg_reference("average", projection=True)
    return raw


register_loader(".bdf", load_bdf)
