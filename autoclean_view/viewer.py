"""Module for loading and visualizing EEGLAB .set files using MNE-QT Browser."""

import os
import sys
from pathlib import Path
import mne
from mne_qt_browser import plot_raw


def load_set_file(file_path):
    """Load an EEGLAB .set file and return an MNE Raw object.
    
    Parameters
    ----------
    file_path : str or Path
        Path to the .set file to load
    
    Returns
    -------
    raw : mne.io.Raw
        The loaded Raw object
    """
    file_path = Path(file_path)
    
    # Validate file exists and has .set extension
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.suffix.lower() != ".set":
        raise ValueError(f"File must have .set extension, got: {file_path}")
    
    try:
        # Load the .set file
        raw = mne.io.read_raw_eeglab(file_path, preload=True)
        
        # Pick common channel types
        raw.pick_types(eeg=True, eog=True, ecg=True, emg=True, misc=True)
        
        return raw
    except Exception as e:
        raise RuntimeError(f"Error loading .set file: {e}") from e


def view_eeg(raw):
    """Display EEG data using MNE-QT Browser.
    
    Parameters
    ----------
    raw : mne.io.Raw
        The Raw object to visualize
    """
    # Set Qt backend to cocoa on macOS for smoother experience
    if sys.platform == "darwin":
        os.environ["QT_QPA_PLATFORM"] = "cocoa"
    
    # Launch the QT Browser
    fig = plot_raw(raw, block=True)
    return fig
