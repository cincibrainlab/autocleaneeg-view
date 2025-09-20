"""AutoCleanEEG-View: A lightweight tool for viewing EEG files (.set, .edf, .bdf) using MNE-QT Browser."""

__version__ = "0.1.6"

from .viewer import load_eeg_file, view_eeg

__all__ = ["load_eeg_file", "view_eeg", "__version__"]
