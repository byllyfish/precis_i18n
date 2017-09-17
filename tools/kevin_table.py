"""
Generate 'Kevin' table for README.
"""

import precis_i18n.codec


letter_k = [ ord('K'), 0x212A, 0xFF2B, 0x039A, 0x1E32, 0x1E34, 0x2C69, 0xA740, 
             0xA742, 0xA744, 0xA7A2, 0x24C0, 0x1F11A, 0x1F13A, 0x1F15A, 0x1F17A]

def _escape(s):
    return s.encode('raw-unicode-escape').decode('ascii').replace('\\', '&#92;')

def _xml_escape(s):
    return s.encode('ascii', errors='xmlcharrefreplace').decode('ascii')


def _column(s):
    try:
        # Leave ASCII strings alone.
        s.encode('ascii')
        return s
    except UnicodeEncodeError:
        pass
    return "%s (%s)" % (_xml_escape(s), _escape(s))



print('Original String|UsernameCasePreserved|UsernameCaseMapped|NicknameCaseMapped')
print('---------------|---------------------|------------------|------------------')

for k in letter_k:
    kevin = chr(k) + 'evin'

    try:
        case_preserved = kevin.encode('UsernameCasePreserved').decode('utf-8')
    except UnicodeEncodeError:
        case_preserved = 'DISALLOWED'

    try:
        case_mapped = kevin.encode('UsernameCaseMapped').decode('utf-8')
    except UnicodeEncodeError:
        case_mapped = 'DISALLOWED'

    nickname = kevin.encode('NicknameCaseMapped').decode('utf-8')

    col1 = _column(kevin)
    col2 = _column(case_preserved)
    col3 = _column(case_mapped)
    col4 = _column(nickname)

    print('%s | %s | %s | %s' % (col1, col2, col3, col4))

