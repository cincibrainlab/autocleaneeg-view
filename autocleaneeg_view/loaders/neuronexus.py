"""NeuroNexus loader plugin via Neo.

This loader uses ``neo.io.NeuroNexusIO`` to read data and converts it into an
``mne.io.RawArray`` for viewing. Neo and Quantities are optional dependencies
and are only required when loading NeuroNexus files.
"""

from __future__ import annotations

import numpy as np
import mne

from . import register_loader
from .neuronexus_remap import apply_channel_remappers
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


def load_neuronexus(path, remap_channels=False):
    """Load NeuroNexus data via Neo and return an MNE RawArray.

    Parameters
    ----------
    path : str | Path
        Path to a NeuroNexus recording.
    remap_channels : bool, optional
        Whether to apply channel remapping. Default is False.
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

        array_ann = getattr(sig, "array_annotations", {})
        if "channel_names" in array_ann:
            chs = array_ann["channel_names"].tolist()
        else:
            chs = [f"{name}-{i}" for i in range(sig.shape[1])]

        channel_ids = None
        for key in (
            "channel_ids",
            "channel_id",
            "channel_indexes",
            "channel_index",
            "channel_indices",
        ):
            if key not in array_ann:
                continue
            candidate = array_ann[key]
            if candidate is None:
                continue
            try:
                candidate_list = candidate.tolist()
            except AttributeError:
                try:
                    candidate_list = list(candidate)
                except TypeError:
                    continue
            try:
                matches = len(candidate_list) == len(chs)
            except TypeError:
                continue
            if not matches:
                continue
            channel_ids = candidate_list
            break

        stream_id = None
        if hasattr(sig, "annotations"):
            stream_id = sig.annotations.get("stream_id")

        if remap_channels:
            indices, mapped_names = apply_channel_remappers(
                stream_id=stream_id,
                signal_name=name,
                channel_ids=channel_ids,
                channel_names=chs,
            )
            if not mapped_names:
                continue
        else:
            # No remapping - use channels as-is
            indices = None
            mapped_names = chs

        is_dimensionless = _is_dimensionless(sig.units)
        data_source = sig
        if not is_dimensionless:
            try:
                data_source = sig.rescale(pq.V)
            except Exception:
                # Keep native units; still viewable as misc
                data_source = sig

        data_block = data_source.magnitude.T
        if indices:
            data_block = data_block[indices, :]

        data_list.append(data_block)
        ch_names.extend(mapped_names)

        if is_dimensionless:
            ch_types.extend(["stim"] * len(mapped_names))
        else:
            stream_label = (stream_id or "").lower() if stream_id else ""
            if stream_label == "ai-pri" or "analog (pri)" in name.lower() or "pri" in name.lower():
                ch_types.extend(["eeg"] * len(mapped_names))
            else:
                ch_types.extend(["misc"] * len(mapped_names))

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
