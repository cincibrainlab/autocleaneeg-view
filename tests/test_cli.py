"""Tests for the CLI interface."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from autocleaneeg_view.cli import main
from autocleaneeg_view import loaders


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


def test_cli_requires_file_argument(runner):
    """Test that CLI requires a file argument."""
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "FILE argument is required unless --list-formats is used." in result.output


def test_cli_shows_help(runner):
    """Test that help flag works."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Load and visualize EEG files" in result.output
    assert "--view" in result.output
    assert "--no-view" in result.output


def test_cli_with_nonexistent_file(runner):
    """Test CLI with a nonexistent file."""
    result = runner.invoke(main, ["nonexistent_file.set"])
    assert result.exit_code != 0
    assert "Error: " in result.output


def test_cli_view_default_and_no_view_flag(runner, monkeypatch):
    """Test default views and --no-view suppresses viewer."""
    view_called = False

    class MockRaw:
        def __init__(self):
            self.ch_names = ["EEG1", "EEG2"]
            self.n_times = 1000
            self.times = [0, 10]
            self.info = {"sfreq": 100}

    def mock_load_eeg_file(file_path):
        return MockRaw()

    def mock_view_eeg(raw):
        nonlocal view_called
        view_called = True

    monkeypatch.setattr("autocleaneeg_view.cli.load_eeg_file", mock_load_eeg_file)
    monkeypatch.setattr("autocleaneeg_view.cli.view_eeg", mock_view_eeg)

    with runner.isolated_filesystem():
        with open("test.set", "w") as f:
            f.write("dummy content")

        # Default behavior: view is launched
        result = runner.invoke(main, ["test.set"])
        assert result.exit_code == 0
        assert view_called


def test_cli_list_formats(runner, monkeypatch):
    """--list-formats prints supported extensions and exits 0."""
    result = runner.invoke(main, ["--list-formats"])
    assert result.exit_code == 0
    assert "Supported file extensions:" in result.output
    for ext in loaders.SUPPORTED_EXTENSIONS:
        assert ext in result.output

    view_called = False

    def mock_load_eeg_file(file_path):
        return object()

    def mock_view_eeg(raw):
        nonlocal view_called
        view_called = True

    monkeypatch.setattr("autocleaneeg_view.cli.load_eeg_file", mock_load_eeg_file)
    monkeypatch.setattr("autocleaneeg_view.cli.view_eeg", mock_view_eeg)

    with runner.isolated_filesystem():
        Path("test.set").touch()
        result = runner.invoke(main, ["test.set", "--no-view"])
        assert result.exit_code == 0
        assert not view_called
        assert "Loaded test.set successfully:" in result.output
        assert "Use --view to visualize the data." in result.output

    view_called = False
    with runner.isolated_filesystem():
        Path("test.set").touch()
        result = runner.invoke(main, ["test.set", "--view"])
        assert result.exit_code == 0
        assert view_called


def test_cli_diagnose_neuronexus(monkeypatch, runner, tmp_path):
    """--diagnose reports NeuroNexus companion-file status accurately."""
    metadata = tmp_path / "subject.xdat.json"
    metadata.write_text("{}")
    data = tmp_path / "subject_data.xdat"
    data.write_text("")
    timestamps = tmp_path / "subject_timestamp.xdat"
    timestamps.write_text("")

    def mock_load_eeg_file(file_path):
        return object()

    monkeypatch.setattr("autocleaneeg_view.cli.load_eeg_file", mock_load_eeg_file)
    monkeypatch.setattr("autocleaneeg_view.cli.view_eeg", lambda raw: None)

    result = runner.invoke(main, [str(metadata), "--no-view", "--diagnose"])
    assert result.exit_code == 0
    assert f"  JSON: {metadata} -> OK" in result.output
    assert f"  DATA: {data} -> OK" in result.output
    assert f"  TIME: {timestamps} -> OK" in result.output

    result = runner.invoke(main, [str(data), "--no-view", "--diagnose"])
    assert result.exit_code == 0
    assert f"  JSON: {metadata} -> OK" in result.output
    assert f"  DATA: {data} -> OK" in result.output
    assert f"  TIME: {timestamps} -> OK" in result.output
