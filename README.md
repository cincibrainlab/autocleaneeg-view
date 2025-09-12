# 🧠 AutoCleanEEG-View

**AutoCleanEEG-View** is a simple yet powerful tool for neuroscientists, researchers, and EEG enthusiasts to visualize EEGLAB `.set`, `.edf`, and `.bdf` files using the modern MNE-QT Browser.

## ✨ Features

- **Simple Interface**: Just one command to view your EEG data
- **Interactive Visualization**: Pan, zoom, filter, and explore your EEG signals
- **Automatic Channel Type Detection**: Properly handles EEG, EOG, ECG channels
- **Event Markers**: View annotations and event markers in your recordings
- **Cross-Platform**: Works on macOS and Linux

## 🚀 Quick Start

### Installation

```bash
pip install autocleaneeg-view
```

### Basic Usage

```bash
# View an EEG file (default behavior)
autoclean-view path/to/yourfile.set

# Explicitly open the viewer (also supported for clarity)
autoclean-view path/to/yourfile.set --view

# Load without viewing (just validate the file)
autoclean-view path/to/yourfile.set --no-view
```

## 🧪 Test With Simulated Data

Don't have EEG data handy? Generate realistic test data to try it out:

```bash
# Generate a 10-second recording with 32 channels
python scripts/generate_test_data.py --output data/simulated_eeg.set

# Quick test all in one step
./scripts/test_with_simulated_data.sh
```

### Simulation Options

Customize your simulated data:

```
python scripts/generate_test_data.py --help
```

- `--duration 60`: Create a 60-second recording
- `--sfreq 512`: Set sampling rate to 512 Hz
- `--channels 64`: Generate 64 channel EEG
- `--no-events`: Disable simulated event markers
- `--no-artifacts`: Generate clean data without eye blinks/artifacts

## 📋 Requirements

- Python 3.9 or higher
- MNE-Python 1.7+
- MNE-QT-Browser 0.5.2+
- PyQt5 (macOS) or compatible Qt backend

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

## 📝 License

[MIT License](LICENSE)
