# Hunt for examples where order of NFC/Casefold makes a difference.

import unicodedata

def case(ch):
    return ch.casefold()

def nfc(ch):
    return unicodedata.normalize('NFC', ch)

def make(ch):
    return '%s%s' % (ch, unicodedata.normalize('NFD', ch))


for i in range(0, 0x010ffff):
    s = make(chr(i))
    if case(nfc(s)) != nfc(case(s)):
        print(s.encode('unicode-escape'))
