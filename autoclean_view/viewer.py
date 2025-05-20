"""Module for loading and visualizing EEGLAB .set files using MNE-QT Browser."""

import os
import sys
from pathlib import Path
import mne


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
        # Try loading as Raw first
        eeg = mne.io.read_raw_eeglab(file_path, preload=True)
        
        # Pick common channel types
        eeg.pick_types(eeg=True, eog=True, ecg=True, emg=True, misc=True)
        
        return eeg
    except Exception as e:
        try:
            # If Raw loading fails, try loading as Epochs
            eeg = mne.io.read_epochs_eeglab(file_path)
            
            return eeg
        except Exception as inner_e:
            raise RuntimeError(f"Error loading .set file: {e}; also tried epochs loader: {inner_e}") from e



def view_eeg(eeg):
    """Display EEG data using MNE-QT Browser.
    
    Parameters
    ----------
    raw : mne.io.Raw
        The Raw object to visualize
    """

    # Launch the QT Browser with auto scaling
    fig = eeg.plot(block=True, scalings='auto')

    return fig
