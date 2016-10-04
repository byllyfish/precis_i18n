# PRECIS Codec: Internationalized Usernames and Passwords

[![Build Status](https://travis-ci.org/byllyfish/precis_codec.svg?branch=master)](https://travis-ci.org/byllyfish/precis_codec) [![codecov.io](https://codecov.io/gh/byllyfish/precis_codec/coverage.svg?branch=master)](https://codecov.io/gh/byllyfish/precis_codec?branch=master)

The PRECIS codec makes internationalized user names and passwords safer for use by applications. 
PRECIS profiles transform unicode strings into a canonical UTF-8 form, suitable for byte-by-byte comparison.

This module implements the PRECIS Framework as described in:

- PRECIS Framework: Preparation, Enforcement, and Comparison of Internationalized Strings in Application Protocols (RFC 7564)
- Preparation, Enforcement, and Comparison of Internationalized Strings Representing Usernames and Passwords (RFC 7613)
- Preparation, Enforcement, and Comparison of Internationalized Strings Representing Nicknames (RFC 7700)

## Usage

Import the `precis_codec` module to register the PRECIS codec names. Use the `encode` method with any unicode string. `encode` will raise a `UnicodeEncodeError` if the string is disallowed.

```python

>>> import precis_codec
>>> 'Kevin'.encode('UsernameCasePreserved')
b'Kevin'
>>> '\u212Aevin'.encode('UsernameCasePreserved')
b'Kevin'
>>> '\uFF2Bevin'.encode('UsernameCasePreserved')
b'Kevin'
>>> '\u212Aevin'.encode('UsernameCaseMapped')
b'kevin'
>>> '\uFF2Bevin'.encode('OpaqueString')
b'\xef\xbc\xabevin'
>>> '\U0001F17Aevin'.encode('UsernameCasePreserved')
Traceback (most recent call last):
    ...
UnicodeEncodeError: 'usernamecasepreserved' codec can't encode character '\U0001f17a' in position 0: FREE_PVAL/symbols

```

## Supported Codecs

Each PRECIS profile has a corresponding codec name. The `CaseMapped` variant converts the string to lower case for implementing case-insensitive comparison.

- UsernameCasePreserved
- UsernameCaseMapped
- Nickname
- OpaqueString

## Examples

There are multiple ways to write "Kevin" by varying only the "K".

Original String|UsernameCasePreserved|UsernameCaseMapped|Nickname
---------------|-----------------|------------------|------------------
Kevin | Kevin | kevin | kevin
&#x212A;evin '\u212Aevin' | Kevin | kevin | kevin
&#xFF2B;evin '\uFF2Bevin' | Kevin | kevin | kevin
&#x039A;evin '\u039Aevin' | &#x039A;evin '\u039Aevin' | &#x03BA;evin '\u03BAevin' | &#x03BA;evin '\u03BAevin'
&#x1e32;evin '\u1E32evin' | &#x1e32;evin '\u1E32evin' | &#x1E33;evin '\u1E33evin' | &#x1E33;evin '\u1E33evin'
&#x1E34;evin '\u1E34evin' | &#x1E34;evin '\u1E34evin' | &#x1E35;evin '\u1E35evin' | &#x1E35;evin '\u1E35evin'
&#x2c69;evin '\u2C69evin' | &#x2c69;evin '\u2C69evin' | &#x2C6A;evin '\u2C6Aevin' | &#x2C6A;evin '\u2C6Aevin'
&#xA740;evin '\uA740evin' | &#xA740;evin '\uA740evin' | &#xA741;evin '\uA741evin' | &#xA741;evin '\uA741evin'
&#xA742;evin '\uA742evin' | &#xA742;evin '\uA742evin' | &#xA743;evin '\uA743evin' | &#xA743;evin '\uA743evin'
&#xA744;evin '\uA744evin' | &#xA744;evin '\uA744evin' | &#xA745;evin '\uA745evin' | &#xA745;evin '\uA745evin'
&#xA7A2;evin '\uA7A2evin' | &#xA7A2;evin '\uA7A2evin' | &#xA7A3;evin '\uA7A3evin' | &#xA7A3;evin '\uA7A3evin'
&#x24C0;evin '\u24C0evin'  | DISALLOWED | DISALLOWED | kevin
&#x1F11A;evin '\U0001F11Aevin' | DISALLOWED | DISALLOWED | (K)evin
&#x1F13A;evin '\U0001F13Aevin' | DISALLOWED | DISALLOWED | Kevin
&#x1F15A;evin '\U0001F15Aevin' | DISALLOWED | DISALLOWED | &#x1F15A;evin '\U0001F15Aevin'
&#x1F17A;evin '\U0001F17Aevin' | DISALLOWED | DISALLOWED | &#x1F17A;evin '\U0001F17Aevin'

## License

MIT License
