"""Tests for the viewer module."""

import os
import sys
from pathlib import Path

import pytest
import mne
import numpy as np

from autoclean_view.viewer import load_set_file, view_eeg


@pytest.fixture
def mock_set_file(tmp_path):
    """Create a mock .set file path for testing."""
    return tmp_path / "test_data.set"


def test_load_set_file_validates_extension(mock_set_file):
    """Test that load_set_file validates the file extension."""
    wrong_ext = Path(str(mock_set_file).replace(".set", ".txt"))
    
    with pytest.raises(ValueError, match="must have .set extension"):
        load_set_file(wrong_ext)


def test_load_set_file_validates_existence(mock_set_file):
    """Test that load_set_file validates file existence."""
    with pytest.raises(FileNotFoundError):
        load_set_file(mock_set_file)  # File doesn't exist yet


def test_load_set_file(monkeypatch, mock_set_file):
    """Test loading a .set file with a monkey-patched MNE function."""
    # Create a mock Raw object
    mock_raw = mne.io.RawArray(np.random.rand(10, 1000), 
                              mne.create_info(10, 100, ch_types='eeg'))
    
    # Monkeypatch mne.io.read_raw_eeglab to return our mock_raw
    def mock_read_raw_eeglab(*args, **kwargs):
        return mock_raw
    
    monkeypatch.setattr(mne.io, "read_raw_eeglab", mock_read_raw_eeglab)
    
    # Create an empty file to pass existence check
    mock_set_file.touch()
    
    # Test loading
    raw = load_set_file(mock_set_file)
    assert raw is mock_raw


def test_view_eeg(monkeypatch, mock_set_file):
    """Test that view_eeg calls plot_raw with the right parameters."""
    # Create a mock Raw object
    mock_raw = mne.io.RawArray(np.random.rand(10, 1000), 
                              mne.create_info(10, 100, ch_types='eeg'))
    
    # Keep track of calls to plot_raw
    plot_calls = []
    
    def mock_plot_raw(raw, block=False):
        plot_calls.append({"raw": raw, "block": block})
        return "mock_figure"
    
    # Monkeypatch the plot_raw function
    monkeypatch.setattr("autoclean_view.viewer.plot_raw", mock_plot_raw)
    
    # Call view_eeg
    result = view_eeg(mock_raw)
    
    # Check that plot_raw was called correctly
    assert len(plot_calls) == 1
    assert plot_calls[0]["raw"] is mock_raw
    assert plot_calls[0]["block"] is True
    assert result == "mock_figure"
    
    # Check that QT_QPA_PLATFORM was set on macOS
    if sys.platform == "darwin":
        assert os.environ.get("QT_QPA_PLATFORM") == "cocoa"
