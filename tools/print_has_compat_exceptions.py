from precis_codec.derived import derived_property
from precis_codec.profile import UsernameCasePreserved
from precis_codec.unicode import UnicodeData

UCD = UnicodeData()
profile = UsernameCasePreserved(UCD)

count = 0
ascii = 0
for cp in range(0, 0x110000):
    _, reason = derived_property(cp, UCD)
    if reason == 'has_compat':
        try:
            result = profile.enforce(chr(cp))
            print('%04x => %s' % (cp, result))

            if len(result) == 1 and result[0] < 128:
                ascii += 1
            count += 1
        except UnicodeEncodeError:
            pass
print('Exceptions: %d, %d ascii' % (count, ascii))
