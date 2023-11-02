import unicodedata

from precis_i18n import get_profile

profile = get_profile("nicknamecasemapped:ToLower")


def _escape(s):
    return s.encode("unicode-escape").decode("ascii")


for cp in range(0x0110000):
    original = chr(cp)
    try:
        actual = profile.enforce(original)
        if actual != original:
            idempotent = profile.enforce(actual)
            if idempotent.strip() != actual.strip():
                print(
                    _escape(original),
                    unicodedata.name(original),
                    ";",
                    unicodedata.decomposition(original),
                )
    except UnicodeEncodeError:
        pass
