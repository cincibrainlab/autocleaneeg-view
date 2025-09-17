"""Unit tests for NeuroNexus channel remapping."""

from autocleaneeg_view.loaders.neuronexus_remap import (
    ChannelNameRemapper,
    DEFAULT_ALLEGO_PRIMARY_REMAP,
    apply_channel_remappers,
)


def test_default_remap_maps_primary_channels_and_drops_unused():
    """Primary analog channels should follow the MEA remapping table."""

    channel_ids = ["30", "28", "2", "31"]
    channel_names = ["pr30", "pr28", "pr02", "pr31"]

    indices, names = apply_channel_remappers(
        stream_id="ai-pri",
        signal_name="NeuroNexus Allego Analog (pri) Data",
        channel_ids=channel_ids,
        channel_names=channel_names,
        remappers=[DEFAULT_ALLEGO_PRIMARY_REMAP],
    )

    assert indices == [0, 1, 3]
    assert names == ["Ch 01", "Ch 02", "Ch 08"]


def test_default_remap_infers_channel_ids_from_primary_names():
    """Channel IDs can be derived from Allego prXX names."""

    channel_names = ["pr30", "pr02", "pr31"]

    indices, names = apply_channel_remappers(
        stream_id="ai-pri",
        signal_name="NeuroNexus Allego Analog (pri) Data",
        channel_ids=None,
        channel_names=channel_names,
        remappers=[DEFAULT_ALLEGO_PRIMARY_REMAP],
    )

    assert indices == [0, 2]
    assert names == ["Ch 01", "Ch 08"]


def test_default_remap_skips_non_primary_streams():
    """Digital streams should preserve their raw channel labels."""

    channel_ids = ["30", "28"]
    channel_names = ["din0", "din1"]

    indices, names = apply_channel_remappers(
        stream_id="din",
        signal_name="NeuroNexus Allego Digital-in (din) Data",
        channel_ids=channel_ids,
        channel_names=channel_names,
        remappers=[DEFAULT_ALLEGO_PRIMARY_REMAP],
    )

    assert indices == [0, 1]
    assert names == channel_names


def test_custom_remapper_can_drop_unmapped_channels():
    """drop_missing=True removes channels that are not listed."""

    remapper = ChannelNameRemapper(
        mapping={"1": "Mapped"},
        stream_ids=("custom",),
        drop_missing=True,
    )

    indices, names = apply_channel_remappers(
        stream_id="custom",
        signal_name=None,
        channel_ids=["1", "2"],
        channel_names=["raw-1", "raw-2"],
        remappers=[remapper],
    )

    assert indices == [0]
    assert names == ["Mapped"]


def test_signal_name_substring_matches_when_stream_id_missing():
    """Remappers may fall back to matching substrings in signal names."""

    remapper = ChannelNameRemapper(
        mapping={"1": "Mapped"},
        stream_ids=(),
        signal_name_substrings=("analog (pri)",),
    )

    indices, names = apply_channel_remappers(
        stream_id=None,
        signal_name="Some Analog (Pri) Recording",
        channel_ids=["1"],
        channel_names=["raw"],
        remappers=[remapper],
    )

    assert indices == [0]
    assert names == ["Mapped"]

