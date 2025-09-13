import mne
from . import register_loader


def load_set(path):
    try:
        return mne.io.read_raw_eeglab(path, preload=True)
    except Exception:
        # Fallback: maybe it's an Epochs file
        return mne.io.read_epochs_eeglab(path)


register_loader(".set", load_set)
