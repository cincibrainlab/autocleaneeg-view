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
@click.option(
    "--diagnose",
    is_flag=True,
    help="Run a quick NeuroNexus (.xdat) companion-file check before loading.",
)
def main(file, view, list_formats, diagnose):
    """Load and visualize EEG files using MNE-QT Browser.

    FILE is the path to the EEG file to process.
    """
    try:
        if list_formats:
            exts = ", ".join(loaders.SUPPORTED_EXTENSIONS)
            click.echo(f"Supported file extensions: {exts}")
            return 0

        # Resolve directory inputs: prefer single .xdat.json in directory.
        from pathlib import Path as _Path
        p = _Path(file)
        if p.is_dir():
            # Prefer composite .xdat.json candidates
            cands = [
                q for q in sorted(p.iterdir()) if q.is_file() and q.name.lower().endswith(".xdat.json")
            ]
            if len(cands) == 1:
                file = str(cands[0])
            elif len(cands) > 1:
                click.echo("Multiple .xdat.json files found; please choose one:")
                for q in cands:
                    click.echo(f"  - {q.name}")
                return 2
            else:
                # Fall back to any single supported format in directory
                exts = set(loaders.SUPPORTED_EXTENSIONS)
                files = [q for q in sorted(p.iterdir()) if q.is_file() and any(q.name.lower().endswith(ext) for ext in exts)]
                if len(files) == 1:
                    file = str(files[0])
                else:
                    click.echo("Could not uniquely resolve a file in directory. Supported extensions:")
                    click.echo(", ".join(loaders.SUPPORTED_EXTENSIONS))
                    return 2

        if diagnose:
            # Lightweight companion checks for .xdat inputs
            _name = str(file).lower()
            if _name.endswith(".xdat") or _name.endswith(".xdat.json"):
                base = _name[:-len(".xdat.json")] if _name.endswith(".xdat.json") else _name[:-len(".xdat")]
                import os as _os
                dirn = _os.path.dirname(str(file))
                exp_json = _os.path.join(dirn, base.split("/")[-1] + ".xdat.json")
                exp_data = _os.path.join(dirn, base.split("/")[-1] + "_data.xdat")
                exp_ts = _os.path.join(dirn, base.split("/")[-1] + "_timestamp.xdat")
                click.echo("Companion files check:")
                click.echo(f"  JSON: {exp_json} -> {'OK' if _os.path.exists(exp_json) else 'MISSING'}")
                click.echo(f"  DATA: {exp_data} -> {'OK' if _os.path.exists(exp_data) else 'MISSING'}")
                click.echo(f"  TIME: {exp_ts} -> {'OK' if _os.path.exists(exp_ts) else 'MISSING'}")

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
