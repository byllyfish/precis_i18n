
from precis_i18n import get_profile
import unicodedata

profile = get_profile('nicknamecasemapped:ToLower')


def _escape(s):
    return s.encode('unicode-escape').decode('ascii')

for cp in range(0x03d3, 0x03d5):
    original = chr(cp)
    try:
        actual = profile.enforce(original).decode('utf-8')
        if actual != original:
            idempotent = profile.enforce(actual).decode('utf-8')
            if idempotent.strip() != actual.strip():
                print(_escape(original), original, _escape(actual), _escape(idempotent), ';', unicodedata.decomposition(original))
    except UnicodeEncodeError:
        pass

