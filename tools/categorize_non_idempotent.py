import unicodedata
from collections import Counter

import precis_i18n as precis


def _escape(s):
    return s.encode('unicode-escape').decode('ascii')


def _idempotent_ignoring_space(profile, value):
    result1 = profile.enforce(value)
    result2 = profile.enforce(result1)
    return result1.strip() == result2.strip()


results = Counter()
profile = precis.get_profile('NicknameCaseMapped:ToLower')

for cp in range(0x0110000):
    char = chr(cp)
    try:
        if not _idempotent_ignoring_space(profile, char):
            decomp = unicodedata.decomposition(char)
            kind = decomp.split()[0]
            if kind.startswith('<'):
                results[kind] += 1
            else:
                print(_escape(char), unicodedata.name(char))
    except UnicodeEncodeError:
        pass

print(results)
