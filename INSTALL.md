# Installation Guide

## Prerequisites

Before installing AutoCleanEEG-View, make sure you have:

- Python 3.9 or higher
- pip or uv for package management

## Installation

### Option 1: Install from PyPI (Recommended)

Once the package is published to PyPI, you can install it using:

```bash
pip install autocleaneeg-view
```

Or with uv:

```bash
uv pip install autocleaneeg-view
```

### Option 2: Install from Source

To install from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/autocleaneeg-view.git
   cd autocleaneeg-view
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

   Or with uv:
   ```bash
   uv pip install -e .
   ```

## Environment Setup

For macOS users, the package will automatically use PyQt5 with the "cocoa" platform for smooth rendering.

For Linux users, if you encounter issues with the default Qt backend, you can try installing PySide2:

```bash
pip install pyside2
```

## Testing Your Installation

After installation, you can verify it works by running:

```bash
autocleaneeg-view --help
# Legacy command
autoclean-view --help
```

This should display the help information for the command-line interface.

## Running Tests

To run the test suite:

1. Install the development dependencies:
   ```bash
   pip install pytest
   ```

2. Run the tests:
   ```bash
   pytest
   ```