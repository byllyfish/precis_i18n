"""
Registers precis_i18n codec.
"""

import codecs
from precis_i18n import (usernamecasepreserved, usernamecasemapped, opaquestring, nickname)


def _make_encode(profile):
    def encode(input, errors='strict'):
        if errors != 'strict':
            raise ValueError('invalid errors argument')
        return (profile.enforce(input), len(input))

    return encode


def _not_supported(input, errors='strict'):
    raise NotImplementedError('decode not supported')


_codecs = { p.name.lower(): p for p in (usernamecasepreserved, usernamecasemapped, opaquestring, nickname) }


def search(name):
    """ Search function to register for PRECIS codecs.
    """
    profile = _codecs.get(name)
    if profile:
        return codecs.CodecInfo(
            name=name,
            encode=_make_encode(profile),
            decode=_not_supported)
    return None


codecs.register(search)
