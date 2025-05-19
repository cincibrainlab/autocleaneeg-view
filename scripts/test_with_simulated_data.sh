#!/bin/bash
# Script to test the autoclean-view package with simulated data

set -e  # Exit on error

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the package in development mode
echo "Installing autoclean-view in development mode..."
pip install -e .

# Create data directory if it doesn't exist
mkdir -p data

# Generate simulated EEG data
echo "Generating simulated EEG data..."
python scripts/generate_test_data.py --duration 10 --channels 32 --output data/simulated_eeg.set

# Run the autoclean-view command
echo "Running autoclean-view with the simulated data..."
autoclean-view data/simulated_eeg.set --view

# Deactivate the virtual environment
deactivate