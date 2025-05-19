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
        raw = load_set_file(file)
        
        if view:
            # Launch the viewer
            view_eeg(raw)
        else:
            # Just print basic info about the loaded file
            click.echo(f"Loaded {file} successfully:")
            click.echo(f"  {len(raw.ch_names)} channels, {raw.n_times} samples")
            click.echo(f"  Duration: {raw.times[-1]:.1f} seconds")
            click.echo(f"  Sampling rate: {raw.info['sfreq']} Hz")
            click.echo("\nUse --view to visualize the data.")
        
        return 0
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
