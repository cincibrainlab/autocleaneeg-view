"""Tests for the CLI interface."""

import pytest
from click.testing import CliRunner

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
    assert "Missing argument 'FILE'" in result.output


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


def test_cli_list_formats(runner):
    """--list-formats prints supported extensions and exits 0."""
    with runner.isolated_filesystem():
        # Click requires the FILE arg to exist due to Path(exists=True)
        with open("dummy.set", "w") as f:
            f.write("")

        result = runner.invoke(main, ["--list-formats", "dummy.set"])
        assert result.exit_code == 0
        assert "Supported file extensions:" in result.output
        for ext in loaders.SUPPORTED_EXTENSIONS:
            assert ext in result.output

    # Ensure --no-view suppresses viewer and prints guidance
    view_called = False
    with runner.isolated_filesystem():
        with open("test.set", "w") as f:
            f.write("dummy content")

        result = runner.invoke(main, ["test.set", "--no-view"])
        assert result.exit_code == 0
        assert not view_called
        assert "Loaded test.set successfully:" in result.output
        assert "Use --view to visualize the data." in result.output

    # Backwards-compatibility: explicit --view also launches viewer
    view_called = False
    with runner.isolated_filesystem():
        with open("test.set", "w") as f:
            f.write("dummy content")

        result = runner.invoke(main, ["test.set", "--view"])
        assert result.exit_code == 0
        assert view_called
