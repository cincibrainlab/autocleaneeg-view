"""NeuroNexus loader plugin via Neo.

This loader uses ``neo.io.NeuroNexusIO`` to read data and converts it into an
``mne.io.RawArray`` for viewing. Neo and Quantities are optional dependencies
and are only required when loading NeuroNexus files.
"""

from __future__ import annotations

import numpy as np
import mne

from . import register_loader
from pathlib import Path


def _require_neo():
    try:
        import quantities as pq  # type: ignore
        from neo.io import NeuroNexusIO  # type: ignore
    except Exception as e:  # pragma: no cover - dependency error path
        raise ImportError(
            "NeuroNexus loading requires 'neo' and 'quantities' packages. "
            "Install with: pip install 'autocleaneeg-view[neo]'"
        ) from e
    return pq, NeuroNexusIO


def _derive_sidecar_json(p: Path) -> Path | None:
    """Return a plausible sidecar JSON path for a given .xdat file.

    Rules:
    - base.xdat.json
    - base_without_suffix(_data|_timestamp).xdat.json
    """
    name = p.name
    # Try exact base.xdat.json
    cand = p.with_suffix(p.suffix + ".json")
    if cand.exists():
        return cand
    # Drop trailing _data or _timestamp
    if name.endswith("_data.xdat") or name.endswith("_timestamp.xdat"):
        stem = name[: name.rfind("_")]
        cand = p.with_name(f"{stem}.xdat.json")
        if cand.exists():
            return cand
    return None


def load_neuronexus(path):
    """Load NeuroNexus data via Neo and return an MNE RawArray.

    Parameters
    ----------
    path : str | Path
        Path to a NeuroNexus recording.
    """
    pq, NeuroNexusIO = _require_neo()

    p = Path(path)
    # If user passed an .xdat file, try to find the sidecar JSON Neo expects
    if p.suffix.lower() == ".xdat":
        sidecar = _derive_sidecar_json(p)
        if sidecar is not None:
            p = sidecar
        else:
            raise FileNotFoundError(
                f"NeuroNexusIO expects the JSON metadata file; could not find sidecar for {p.name}. "
                f"Looked for {p.name}.json or corresponding base .xdat.json"
            )

    reader = NeuroNexusIO(filename=str(p))
    block = reader.read_block(lazy=False)
    if not block.segments:
        raise RuntimeError(f"No segments found in NeuroNexus file: {path}")
    segment = block.segments[0]

    data_list = []
    ch_names = []
    ch_types = []
    sfreqs = set()

    if not segment.analogsignals:
        raise RuntimeError(f"No analogsignals found in first segment: {path}")

    def _is_dimensionless(u) -> bool:
        try:
            return u.dimensionality.string == "dimensionless"
        except Exception:
            return False

    for sig in segment.analogsignals:
        name = getattr(sig, "name", "sig") or "sig"
        sfreqs.add(float(sig.sampling_rate.rescale(pq.Hz)))
        if not _is_dimensionless(sig.units):
            try:
                sig = sig.rescale(pq.V)
            except Exception:
                # Keep native units; still viewable as misc
                pass
            data_list.append(sig.magnitude.T)
            if "channel_names" in sig.array_annotations:
                chs = sig.array_annotations["channel_names"].tolist()
            else:
                chs = [f"{name}-{i}" for i in range(sig.shape[1])]
            ch_names.extend(chs)
            if "Analog (pri)" in name or "pri" in name.lower():
                ch_types.extend(["eeg"] * len(chs))
            else:
                ch_types.extend(["misc"] * len(chs))
        else:
            data_list.append(sig.magnitude.T)
            if "channel_names" in sig.array_annotations:
                chs = sig.array_annotations["channel_names"].tolist()
            else:
                chs = [f"{name}-{i}" for i in range(sig.shape[1])]
            ch_names.extend(chs)
            ch_types.extend(["stim"] * len(chs))

    if not data_list:
        raise RuntimeError("No compatible signals to build RawArray from NeuroNexus block")
    if len(sfreqs) != 1:
        raise RuntimeError(f"Sampling rates differ across signals: {sorted(sfreqs)}")

    data = np.concatenate(data_list, axis=0)
    sfreq = next(iter(sfreqs))
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(data, info)
    return raw


# Register common extensions associated with NeuroNexus exports if present.
# If your data uses a different suffix, you can register another alias here.
register_loader(".nnx", load_neuronexus)
register_loader(".nex", load_neuronexus)
register_loader(".xdat", load_neuronexus)
register_loader(".xdat.json", load_neuronexus)
