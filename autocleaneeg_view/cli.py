"""Command-line interface for AutoCleanEEG-View.

Load and visualize EEG files using the MNE-QT Browser.
"""

import sys
from pathlib import Path

import click

from autocleaneeg_view.viewer import load_eeg_file, view_eeg
from autocleaneeg_view import loaders


@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--view/--no-view",
    default=True,
    help="Launch the MNE-QT Browser to view the data (default: view; use --no-view to suppress).",
)
@click.option(
    "--list-formats",
    is_flag=True,
    help="List supported file extensions and exit.",
)
def main(file, view, list_formats):
    """Load and visualize EEG files using MNE-QT Browser.

    FILE is the path to the EEG file to process.
    """
    try:
        if list_formats:
            exts = ", ".join(loaders.SUPPORTED_EXTENSIONS)
            click.echo(f"Supported file extensions: {exts}")
            return 0

        # Load the EEG file
        eeg = load_eeg_file(file)
        if view:
            # Launch the viewer by default
            view_eeg(eeg)
        else:
            # Just print basic info about the loaded file
            click.echo(f"Loaded {file} successfully:")
            click.echo("Use --view to visualize the data.")

        return 0

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

# Dynamically augment help with supported formats for --help output
try:
    _exts = ", ".join(loaders.SUPPORTED_EXTENSIONS)
    main.__doc__ = (
        (main.__doc__ or "").rstrip() +
        f"\n\nSupported file extensions: {_exts}\n"
    )
except Exception:
    pass
