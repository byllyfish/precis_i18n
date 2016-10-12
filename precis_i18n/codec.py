"""
Registers precis_i18n codec.
"""

import codecs
from precis_i18n import get_profile


def _make_encode(profile):
    def encode(input, errors='strict'):
        if errors != 'strict':
            raise ValueError('invalid errors argument')
        return (profile.enforce(input), len(input))

    return encode


def _not_supported(input, errors='strict'):
    raise NotImplementedError('decode not supported')


def search(name):
    """ Search function to register for PRECIS codecs.
    """
    return codecs.CodecInfo(
        name=name,
        encode=_make_encode(get_profile(name)),
        decode=_not_supported)


codecs.register(search)
