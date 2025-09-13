"""Tests for the viewer module."""

import os
import sys

import pytest
import mne
import numpy as np

import autocleaneeg_view.viewer as viewer
from autocleaneeg_view.viewer import SUPPORTED_EXTENSIONS, load_eeg_file, view_eeg
from autocleaneeg_view import loaders


@pytest.fixture
def mock_raw():
    """Return a simple mock Raw object."""
    return mne.io.RawArray(
        np.random.rand(10, 1000), mne.create_info(10, 100, ch_types="eeg")
    )


def test_load_eeg_file_validates_extension(tmp_path):
    """Test that load_eeg_file validates the file extension."""
    wrong_ext = tmp_path / "test_data.txt"
    wrong_ext.touch()

    with pytest.raises(ValueError) as excinfo:
        load_eeg_file(wrong_ext)

    msg = str(excinfo.value)
    assert "must have one of" in msg
    for ext in SUPPORTED_EXTENSIONS:
        assert ext in msg


def test_load_eeg_file_validates_existence(tmp_path):
    """Test that load_eeg_file validates file existence."""
    missing_file = tmp_path / "test_data.set"
    with pytest.raises(FileNotFoundError):
        load_eeg_file(missing_file)  # File doesn't exist yet


_PARAMS = [
    (".set", "read_raw_eeglab", False),
    (".edf", "read_raw_edf", False),
    (".bdf", "read_raw_bdf", False),
    (".vhdr", "read_raw_brainvision", False),
    (".fif", "read_raw_fif", False),
    (".raw", "read_raw_egi", False),
    (".gdf", "read_raw_gdf", False),
]
if hasattr(mne.io, "read_raw_mff"):
    _PARAMS.append((".mff", "read_raw_mff", True))


@pytest.mark.parametrize("ext, loader_name, is_dir", _PARAMS)
def test_load_eeg_file(monkeypatch, tmp_path, ext, loader_name, is_dir, mock_raw):
    """Ensure each supported format is loaded with the appropriate reader."""

    def mock_loader(*args, **kwargs):
        return mock_raw

    # Patch the reader registry so load_eeg_file uses the mock.
    monkeypatch.setitem(loaders.READERS, ext, mock_loader)

    file_path = tmp_path / f"test{ext}"
    if is_dir:
        file_path.mkdir()
    else:
        file_path.touch()

    raw = load_eeg_file(file_path)
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

