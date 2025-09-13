"""Command-line interface for AutoCleanEEG-View."""

import sys
from pathlib import Path

import click

from autocleaneeg_view.viewer import load_eeg_file, view_eeg


@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--view/--no-view",
    default=True,
    help="Launch the MNE-QT Browser to view the data (default: view; use --no-view to suppress).",
)
def main(file, view):
    """Load and visualize EEG files (.set, .edf, .bdf, .vhdr, .fif, .raw, .gdf and optionally .mff) using MNE-QT Browser.

    FILE is the path to the EEG file to process.
    """
    try:
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
