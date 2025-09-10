"""Tests for the viewer module."""

import os
import sys
from pathlib import Path

import pytest
import mne
import numpy as np

from autoclean_view.viewer import load_eeg_file, view_eeg


@pytest.fixture
def mock_set_file(tmp_path):
    """Create a mock .set file path for testing."""
    return tmp_path / "test_data.set"


@pytest.fixture
def mock_edf_file(tmp_path):
    """Create a mock .edf file path for testing."""
    return tmp_path / "test_data.edf"


@pytest.fixture
def mock_bdf_file(tmp_path):
    """Create a mock .bdf file path for testing."""
    return tmp_path / "test_data.bdf"


def test_load_eeg_file_validates_extension(mock_set_file):
    """Test that load_eeg_file validates the file extension."""
    wrong_ext = Path(str(mock_set_file).replace(".set", ".txt"))

    with pytest.raises(
        ValueError, match="must have .set, .edf, or .bdf extension"
    ):
        load_eeg_file(wrong_ext)


def test_load_eeg_file_validates_existence(mock_set_file):
    """Test that load_eeg_file validates file existence."""
    with pytest.raises(FileNotFoundError):
        load_eeg_file(mock_set_file)  # File doesn't exist yet


def test_load_eeg_file_set(monkeypatch, mock_set_file):
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
    raw = load_eeg_file(mock_set_file)
    assert raw is mock_raw


def test_load_eeg_file_edf(monkeypatch, mock_edf_file):
    """Test loading an .edf file with a monkey-patched MNE function."""
    mock_raw = mne.io.RawArray(
        np.random.rand(10, 1000), mne.create_info(10, 100, ch_types="eeg")
    )

    def mock_read_raw_edf(*args, **kwargs):
        return mock_raw

    monkeypatch.setattr(mne.io, "read_raw_edf", mock_read_raw_edf)
    mock_edf_file.touch()
    raw = load_eeg_file(mock_edf_file)
    assert raw is mock_raw


def test_load_eeg_file_bdf(monkeypatch, mock_bdf_file):
    """Test loading a .bdf file with a monkey-patched MNE function."""
    mock_raw = mne.io.RawArray(
        np.random.rand(10, 1000), mne.create_info(10, 100, ch_types="eeg")
    )

    def mock_read_raw_bdf(*args, **kwargs):
        return mock_raw

    monkeypatch.setattr(mne.io, "read_raw_bdf", mock_read_raw_bdf)
    mock_bdf_file.touch()
    raw = load_eeg_file(mock_bdf_file)
    assert raw is mock_raw


def test_view_eeg(monkeypatch):
    """Test that view_eeg calls plot with the right parameters."""
    mock_raw = mne.io.RawArray(
        np.random.rand(10, 1000), mne.create_info(10, 100, ch_types="eeg")
    )

    plot_calls = []

    def mock_plot(self, block=False, scalings="auto"):
        plot_calls.append({"self": self, "block": block, "scalings": scalings})
        return "mock_figure"

    monkeypatch.setattr(mne.io.BaseRaw, "plot", mock_plot)

    result = view_eeg(mock_raw)

    assert len(plot_calls) == 1
    assert plot_calls[0]["self"] is mock_raw
    assert plot_calls[0]["block"] is True
    assert plot_calls[0]["scalings"] == "auto"
    assert result == "mock_figure"

    if sys.platform == "darwin":
        assert os.environ.get("QT_QPA_PLATFORM") == "cocoa"
