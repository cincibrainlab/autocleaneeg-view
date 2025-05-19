"""Command-line interface for AutoClean-View."""

import sys
from pathlib import Path
import click

from autoclean_view.viewer import load_set_file, view_eeg


@click.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--view', is_flag=True, help="Launch the MNE-QT Browser to view the data.")
def main(file, view):
    """Load and visualize EEGLAB .set files using MNE-QT Browser.
    
    FILE is the path to the .set file to process.
    """
    try:
        # Load the .set file
        eeg = load_set_file(file)
        if view:
            # Launch the viewer
            view_eeg(eeg)
        else:
            # Just print basic info about the loaded file
            click.echo(f"Loaded {file} successfully:")
        
        return 0
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
