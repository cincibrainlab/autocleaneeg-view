"""Channel remapping utilities for NeuroNexus streams.

This module centralises the logic for renaming or dropping NeuroNexus
channels after they have been read via ``neo``.  The goal is to keep the
transformation data-driven so that projects with different Allego probes or
custom wiring layouts can tweak the remapping tables without touching the core
loader.

The default configuration mirrors the ``xdat2meaLookup`` helper that ships
with the vendor-supplied MATLAB importer.  It renames the primary analog
(``ai-pri``) channels so that they follow the MEA convention (``Ch 01`` … ``Ch
30``) instead of the raw Allego labels (``prX``), and it removes the two
hardware channels that are normally discarded during MATLAB preprocessing.

To adapt the behaviour for a different probe:

* copy :data:`DEFAULT_ALLEGO_PRIMARY_REMAP` and adjust the mapping table or
  the ``drop_ids`` list;
* append the modified instance to
  :data:`NEURONEXUS_CHANNEL_REMAPPERS` so it is picked up automatically; or
* call :func:`apply_channel_remappers` directly from a bespoke loader and pass
  your own ``remappers`` sequence.

The rest of the loader only needs to import
:func:`apply_channel_remappers`—everything else lives in this file so that the
rules are easy to audit and extend.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

RemapIndices = tuple[int, ...]
RemapNames = tuple[str, ...]
RemapIds = tuple[str, ...]


_PR_CHANNEL_SUFFIX_RE = re.compile(r"(\d+)(?!.*\d)")


def _coerce_to_str(token: object | None) -> str:
    """Return ``token`` as a normalised string."""

    if token is None:
        return ""
    if isinstance(token, bytes):
        return token.decode(errors="ignore").strip()
    return str(token).strip()


def _normalise_token(token: object | None) -> str:
    """Lower-case token used for comparisons (stream IDs, substrings)."""

    return _coerce_to_str(token).lower()


def _normalise_channel_id(token: object | None) -> str:
    """Normalise a channel identifier to ease dictionary lookups."""

    raw = _coerce_to_str(token)
    if not raw:
        return ""
    if raw.isdigit():
        # Normalise numeric identifiers so ``"03"`` and ``3`` collide.
        return str(int(raw))
    return raw.lower()


def _infer_ids_from_names(channel_names: Sequence[str]) -> RemapIds | None:
    """Derive channel IDs from Allego style names when IDs are missing."""

    tokens = [_coerce_to_str(name) for name in channel_names]
    if not tokens:
        return None

    lowered = [token.lower() for token in tokens]
    if all(token.isdigit() for token in tokens):
        return tuple(str(int(token)) for token in tokens)

    if not any(token.startswith("pr") for token in lowered):
        return None

    inferred: list[str] = []
    for token, low in zip(tokens, lowered):
        if not low.startswith("pr"):
            return None
        match = _PR_CHANNEL_SUFFIX_RE.search(token)
        if match is None:
            return None
        suffix = str(int(match.group(1)))
        if low.startswith("pri"):
            inferred.append(f"pri_{suffix}")
        else:
            inferred.append(suffix)

    return tuple(inferred)


@dataclass
class RemapResult:
    """Outcome of a remapping step."""

    keep_indices: RemapIndices
    names: RemapNames
    channel_ids: RemapIds

    def __post_init__(self) -> None:  # pragma: no cover - defensive programming
        expected = len(self.keep_indices)
        if expected != len(self.names) or expected != len(self.channel_ids):
            raise ValueError("RemapResult indices/name length mismatch")


@dataclass
class ChannelNameRemapper:
    """Describe how to rename/drop channels for a given stream."""

    mapping: Mapping[str, str]
    label: str = "custom"
    stream_ids: tuple[str, ...] = ("ai-pri",)
    signal_name_substrings: tuple[str, ...] = ()
    drop_ids: Iterable[str] = ()
    drop_missing: bool = False
    description: str | None = None

    def __post_init__(self) -> None:
        self.mapping = {  # type: ignore[assignment]
            _normalise_channel_id(key): value for key, value in self.mapping.items()
        }
        self.stream_ids = tuple(_normalise_token(s) for s in self.stream_ids)
        self.signal_name_substrings = tuple(
            _normalise_token(s) for s in self.signal_name_substrings
        )
        self.drop_ids = tuple(_normalise_channel_id(s) for s in self.drop_ids)

    # ------------------------------------------------------------------
    # Remapper selection helpers
    # ------------------------------------------------------------------
    def _matches_stream(self, stream_id: str | None) -> bool:
        if not self.stream_ids:
            return True
        normalised = _normalise_token(stream_id)
        return bool(normalised) and normalised in self.stream_ids

    def _matches_signal_name(self, signal_name: str | None) -> bool:
        if not self.signal_name_substrings:
            return False
        name = _normalise_token(signal_name)
        return any(sub and sub in name for sub in self.signal_name_substrings)

    def applies(self, stream_id: str | None, signal_name: str | None) -> bool:
        """Return ``True`` when the remapper should be used."""

        if self._matches_stream(stream_id):
            return True
        return self._matches_signal_name(signal_name)

    # ------------------------------------------------------------------
    # Remapping
    # ------------------------------------------------------------------
    def remap(
        self,
        *,
        stream_id: str | None,
        signal_name: str | None,
        channel_ids: Sequence[object] | None,
        channel_names: Sequence[str],
    ) -> RemapResult | None:
        """Rename/drop channels if the remapper applies."""

        if not self.applies(stream_id, signal_name):
            return None

        ids: RemapIds | None = None
        if channel_ids is not None and len(channel_ids) == len(channel_names):
            ids = tuple(_normalise_channel_id(raw_id) for raw_id in channel_ids)
        else:
            ids = _infer_ids_from_names(channel_names)

        if ids is None or len(ids) != len(channel_names):
            # Without channel identifiers we cannot map to MEA positions.
            return None

        keep: list[int] = []
        names: list[str] = []
        kept_ids: list[str] = []
        drop_ids = set(self.drop_ids)

        for idx, (chan_id, fallback_name) in enumerate(zip(ids, channel_names)):
            alias = None
            fallback_label = _coerce_to_str(fallback_name)
            fallback_low = fallback_label.lower()
            if fallback_low.startswith("pri"):
                match = _PR_CHANNEL_SUFFIX_RE.search(fallback_label)
                if match is not None:
                    alias = f"pri_{int(match.group(1))}"

            should_drop = False
            if alias is not None:
                should_drop = alias in drop_ids
            else:
                should_drop = chan_id in drop_ids
            if should_drop:
                continue

            mapped = None
            if alias is not None:
                mapped = self.mapping.get(alias)
            if mapped is None:
                mapped = self.mapping.get(chan_id)
            if mapped is None:
                if self.drop_missing:
                    continue
                mapped = fallback_label

            keep.append(idx)
            names.append(mapped)
            kept_ids.append(chan_id)

        return RemapResult(
            keep_indices=tuple(keep),
            names=tuple(names),
            channel_ids=tuple(kept_ids),
        )


def apply_channel_remappers(
    *,
    stream_id: str | None,
    signal_name: str | None,
    channel_ids: Sequence[object] | None,
    channel_names: Sequence[str],
    remappers: Sequence[ChannelNameRemapper] | None = None,
) -> tuple[list[int], list[str]]:
    """Apply the registered remappers and return selected indices and names."""

    names: list[str] = [_coerce_to_str(name) for name in channel_names]
    if not names:
        return ([], [])

    indices = list(range(len(names)))
    ids = (
        [_normalise_channel_id(raw_id) for raw_id in channel_ids]
        if channel_ids is not None
        else None
    )
    candidates = remappers if remappers is not None else NEURONEXUS_CHANNEL_REMAPPERS

    for remapper in candidates:
        result = remapper.remap(
            stream_id=stream_id,
            signal_name=signal_name,
            channel_ids=ids,
            channel_names=names,
        )
        if result is None:
            continue

        indices = [indices[i] for i in result.keep_indices]
        names = list(result.names)
        ids = list(result.channel_ids)

    return indices, names


_ALLEGO_PRIMARY_BASE_MAPPING = {
    "30": "Ch 01",
    "28": "Ch 02",
    "26": "Ch 03",
    "24": "Ch 04",
    "22": "Ch 05",
    "20": "Ch 06",
    "18": "Ch 07",
    "31": "Ch 08",
    "29": "Ch 09",
    "27": "Ch 10",
    "25": "Ch 11",
    "23": "Ch 12",
    "21": "Ch 13",
    "19": "Ch 14",
    "17": "Ch 15",
    "15": "Ch 16",
    "13": "Ch 17",
    "11": "Ch 18",
    "9": "Ch 19",
    "7": "Ch 20",
    "5": "Ch 21",
    "3": "Ch 22",
    "1": "Ch 23",
    "16": "Ch 24",
    "14": "Ch 25",
    "12": "Ch 26",
    "10": "Ch 27",
    "8": "Ch 28",
    "6": "Ch 29",
    "4": "Ch 30",
}

_ALLEGO_PRIMARY_PRI_MAPPING = {f"pri_{idx}": f"Ch {idx + 1:02d}" for idx in range(30)}

_ALLEGO_PRIMARY_MAPPING = {
    **_ALLEGO_PRIMARY_BASE_MAPPING,
    **_ALLEGO_PRIMARY_PRI_MAPPING,
}


DEFAULT_ALLEGO_PRIMARY_REMAP = ChannelNameRemapper(
    label="allego_primary_30ch",
    description="Map Allego primary analog channel IDs to MEA labels (Ch 01–Ch 30)",
    mapping=_ALLEGO_PRIMARY_MAPPING,
    stream_ids=("ai-pri",),
    signal_name_substrings=("analog (pri)",),
    drop_ids=("2", "32", "pri_2", "pri_30", "pri_31"),
)


NEURONEXUS_CHANNEL_REMAPPERS: list[ChannelNameRemapper] = [DEFAULT_ALLEGO_PRIMARY_REMAP]


__all__ = [
    "ChannelNameRemapper",
    "DEFAULT_ALLEGO_PRIMARY_REMAP",
    "NEURONEXUS_CHANNEL_REMAPPERS",
    "RemapResult",
    "RemapIds",
    "apply_channel_remappers",
]
