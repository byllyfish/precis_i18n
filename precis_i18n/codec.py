"""Registers precis_i18n codec."""

import codecs

from precis_i18n import get_profile


def _make_encode(profile):
    def _encode(input, errors="strict"):
        if errors != "strict":
            raise ValueError("invalid errors argument")
        return (profile.enforce(input).encode("utf-8"), len(input))

    return _encode


def _not_supported(input, errors="strict"):
    # pylint: disable=unused-argument
    raise NotImplementedError("decode not supported")


def search(name):
    """Search function registered for PRECIS codecs.

    Args:
        name (str): Codec name.

    Returns:
        CodecInfo: Encode/decode information or None if not found.
    """
    try:
        profile = get_profile(name)
    except KeyError:
        return None

    return codecs.CodecInfo(
        name=name, encode=_make_encode(profile), decode=_not_supported
    )


codecs.register(search)
