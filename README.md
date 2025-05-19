# AutoClean-View

**AutoClean-View** is a lightweight Python package for visualizing EEGLAB `.set` files using the modern MNE-QT Browser.

## Features
- Load `.set` EEG files
- View using MNE's interactive Qt-based signal browser
- Easy CLI interface: `autoclean-view yourfile.set --view`
- Built on MNE-Python and mne-qt-browser

## Installation
```bash
pip install autoclean-view
```

## Usage
```bash
autoclean-view path/to/yourfile.set --view
```

## Test with Simulated Data
The package includes scripts to generate and test with simulated EEG data:

1. Generate simulated data:
   ```bash
   python scripts/generate_test_data.py --output data/simulated_eeg.set
   ```

2. Or run the all-in-one test script:
   ```bash
   ./scripts/test_with_simulated_data.sh
   ```

### Simulation Options
```
python scripts/generate_test_data.py --help
```

Options include:
- `--duration`: Length of simulated recording (seconds)
- `--sfreq`: Sampling frequency (Hz)
- `--channels`: Number of EEG channels
- `--no-events`: Disable simulated events
- `--no-artifacts`: Disable simulated artifacts

## Requirements
- Python 3.9+
- macOS or Linux
- PyQt5 or compatible Qt backend

## License
MIT License