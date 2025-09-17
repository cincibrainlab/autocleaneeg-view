# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoCleanEEG-View is a lightweight tool for visualizing EEG files using the MNE-QT Browser. It provides a simple CLI interface to load and view various EEG file formats including EEGLAB (.set), EDF/BDF, BrainVision, EGI, MNE-FIF, and NeuroNexus formats.

## Development Commands

### Installation and Setup
```bash
# Using uv (preferred for speed)
uv pip install -e .

# Or using pip
pip install -e .
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_viewer.py

# Run with coverage
pytest --cov=autocleaneeg_view
```

### Generating Test Data
```bash
# Generate simulated EEG data for testing
python scripts/generate_test_data.py --output data/simulated_eeg.set

# Quick test with simulated data
./scripts/test_with_simulated_data.sh
```

### Building and Distribution
```bash
# Build package
python -m build

# Install from source
pip install -e .
```

## Architecture

### Plugin-Based Loader System
The core architecture uses a plugin registry pattern in `autocleaneeg_view/loaders/`:
- Each file format has its own loader module (e.g., `edf.py`, `fif.py`, `neuronexus.py`)
- Loaders self-register with the central registry via `register_loader(extension, loader_func)`
- The viewer module (`viewer.py`) dispatches to the appropriate loader based on file extension
- All loaders return MNE Raw or Epochs objects for uniform visualization

### Key Components

**CLI Entry Point** (`cli.py`):
- Handles command-line arguments and options
- Resolves file paths including directory inputs (prefers .xdat.json files)
- Provides diagnostic tools for NeuroNexus companion files
- Delegates to viewer module for loading and display

**Viewer Module** (`viewer.py`):
- `load_eeg_file()`: Main loading function that detects format and dispatches to appropriate loader
- `validate_loader_output()`: Ensures consistent channel selection across all formats
- `view_eeg()`: Launches MNE-QT Browser with platform-specific settings (e.g., cocoa for macOS)
- Supports both Raw (continuous) and Epochs (segmented) data

**Loader Plugins** (`loaders/`):
- Each loader handles format-specific logic and quirks
- NeuroNexus loader uses Neo library and handles complex multi-file scenarios
- All loaders convert to MNE's Raw or Epochs format for consistent downstream processing

### Multi-Part Extension Support
The system supports complex extensions like `.xdat.json` through longest-match detection in `_detect_extension()`, allowing proper handling of multi-part file suffixes.

## Supported Formats

- `.set` - EEGLAB format
- `.edf`, `.bdf` - European Data Format
- `.vhdr` - BrainVision format
- `.fif` - MNE native format (supports both Raw and Epochs)
- `.raw`, `.mff` - EGI formats
- `.gdf` - General Data Format
- `.xdat`, `.xdat.json`, `.nnx`, `.nex` - NeuroNexus formats via Neo

## Command Usage

```bash
# Basic viewing (default behavior)
autocleaneeg-view path/to/file.set

# Load without viewing (validation only)
autocleaneeg-view path/to/file.edf --no-view

# List supported formats
autocleaneeg-view --list-formats

# Diagnose NeuroNexus companion files
autocleaneeg-view path/to/file.xdat --diagnose
```

## Testing Strategy

Tests are split into:
- `test_viewer.py`: Unit tests for loader validation, file detection, and viewer functions
- `test_cli.py`: CLI interface testing including argument parsing and error handling

The test suite uses mocking extensively to avoid dependencies on actual EEG files or GUI components.

## Platform Considerations

- macOS: Sets `QT_QPA_PLATFORM=cocoa` for smooth Qt rendering
- All platforms: Uses `scalings="auto"` for automatic signal scaling in viewer