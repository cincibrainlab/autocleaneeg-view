"""Module for loading and visualizing EEG files using MNE-QT Browser."""

import os
import sys
from pathlib import Path

import mne


SUPPORTED_EXTENSIONS = {".set", ".edf", ".bdf"}


def load_eeg_file(file_path):
    """Load an EEG file and return an MNE Raw or Epochs object.

    Parameters
    ----------
    file_path : str or Path
        Path to the EEG file to load. Supported extensions are ``.set``,
        ``.edf`` and ``.bdf``.

    Returns
    -------
    raw : mne.io.Raw | mne.Epochs
        The loaded object.
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()

    # Validate extension first so users get informative errors even if the
    # file does not exist.
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"File must have .set, .edf, or .bdf extension, got: {file_path}"
        )

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        if ext == ".set":
            eeg = mne.io.read_raw_eeglab(file_path, preload=True)
        elif ext == ".edf":
            eeg = mne.io.read_raw_edf(file_path, preload=True)
        else:  # .bdf
            eeg = mne.io.read_raw_bdf(file_path, preload=True)

        # Pick common channel types
        eeg.pick_types(eeg=True, eog=True, ecg=True, emg=True, misc=True)
        return eeg
    except Exception as e:  # pragma: no cover - exercised via tests
        if ext == ".set":
            try:
                # If Raw loading fails, try loading as Epochs
                eeg = mne.io.read_epochs_eeglab(file_path)
                return eeg
            except Exception as inner_e:
                raise RuntimeError(
                    f"Error loading {ext} file: {e}; also tried epochs loader: {inner_e}"
                ) from e
        raise RuntimeError(f"Error loading {ext} file: {e}") from e


# Backwards compatibility
def load_set_file(file_path):
    """Alias for :func:`load_eeg_file` for legacy imports."""

    return load_eeg_file(file_path)


def view_eeg(eeg):
    """Display EEG data using MNE-QT Browser.

    Parameters
    ----------
    eeg : mne.io.Raw
        The Raw object to visualize.
    """

    if sys.platform == "darwin":  # pragma: no cover - platform specific
        os.environ.setdefault("QT_QPA_PLATFORM", "cocoa")

    # Launch the QT Browser with auto scaling
    fig = eeg.plot(block=True, scalings="auto")

    return fig
