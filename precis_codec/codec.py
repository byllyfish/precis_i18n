# codec.py

import codecs

from precis_codec.profile import (NicknameCaseMapped, NicknamePreserved,
                                  OpaqueString, UsernameCaseMapped,
                                  UsernamePreserved)
from precis_codec.unicode import UnicodeData

UCD = UnicodeData()


def _make_encode(profile, name):
    obj = profile(UCD, name)

    def encode(input, errors='strict'):
        if errors != 'strict':
            raise ValueError('invalid errors argument')
        return (obj.enforce(input), len(input))

    return encode


def _not_supported(input, errors='strict'):
    raise NotImplementedError('decode not supported')


_codecs = {
    'usernamepreserved': UsernamePreserved,
    'usernamecasemapped': UsernameCaseMapped,
    'opaquestring': OpaqueString,
    'nicknamepreserved': NicknamePreserved,
    'nicknamecasemapped': NicknameCaseMapped
}


def search(name):
    profile = _codecs.get(name)
    if profile:
        return codecs.CodecInfo(
            name=name,
            encode=_make_encode(profile, name),
            decode=_not_supported)
    return None


codecs.register(search)
