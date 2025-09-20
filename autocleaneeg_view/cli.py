"""Command-line interface for AutoCleanEEG-View.

Load and visualize EEG files using the MNE-QT Browser.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

import click

from autocleaneeg_view.viewer import load_eeg_file, view_eeg
from autocleaneeg_view import loaders


def _neuronexus_companion_paths(path: Path) -> Optional[Tuple[Path, Path, Path]]:
    """Return expected NeuroNexus companion files for a given path."""
    name = path.name.lower()
    if name.endswith(".xdat.json"):
        base_token = path.name[: -len(".xdat.json")]
    elif name.endswith(".xdat"):
        base_token = path.stem
        lowered_stem = base_token.lower()
        if lowered_stem.endswith("_data"):
            base_token = base_token[: -len("_data")]
        elif lowered_stem.endswith("_timestamp"):
            base_token = base_token[: -len("_timestamp")]
    else:
        return None

    parent = path.parent
    json_path = parent / f"{base_token}.xdat.json"
    data_path = parent / f"{base_token}_data.xdat"
    ts_path = parent / f"{base_token}_timestamp.xdat"
    return json_path, data_path, ts_path


@click.command()
@click.argument("file", type=click.Path(exists=True), required=False)
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
@click.option(
    "--remap-channels",
    is_flag=True,
    help="Apply channel remapping for NeuroNexus files (default: no remapping).",
)
def main(file, view, list_formats, diagnose, remap_channels):
    """Load and visualize EEG files using MNE-QT Browser.

    FILE is the path to the EEG file to process.
    """
    if list_formats:
        exts = ", ".join(loaders.SUPPORTED_EXTENSIONS)
        click.echo(f"Supported file extensions: {exts}")
        return 0

    if file is None:
        raise click.UsageError("FILE argument is required unless --list-formats is used.")

    try:
        path = Path(file)
        if path.is_dir():
            # Prefer composite .xdat.json candidates
            cands = [
                q for q in sorted(path.iterdir()) if q.is_file() and q.name.lower().endswith(".xdat.json")
            ]
            if len(cands) == 1:
                file = str(cands[0])
                path = cands[0]
            elif len(cands) > 1:
                click.echo("Multiple .xdat.json files found; please choose one:")
                for q in cands:
                    click.echo(f"  - {q.name}")
                return 2
            else:
                # Fall back to any single supported format in directory
                exts = set(loaders.SUPPORTED_EXTENSIONS)
                files = [
                    q
                    for q in sorted(path.iterdir())
                    if q.is_file() and any(q.name.lower().endswith(ext) for ext in exts)
                ]
                if len(files) == 1:
                    file = str(files[0])
                    path = files[0]
                else:
                    click.echo("Could not uniquely resolve a file in directory. Supported extensions:")
                    click.echo(", ".join(loaders.SUPPORTED_EXTENSIONS))
                    return 2

        if diagnose:
            companions = _neuronexus_companion_paths(path)
            if companions:
                click.echo("Companion files check:")
                for label, candidate in (
                    ("JSON", companions[0]),
                    ("DATA", companions[1]),
                    ("TIME", companions[2]),
                ):
                    status = "OK" if candidate.exists() else "MISSING"
                    click.echo(f"  {label}: {candidate} -> {status}")

        # Load the EEG file
        eeg = load_eeg_file(file, remap_channels=remap_channels)
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
