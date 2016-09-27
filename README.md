# PRECIS Codec: Internationalized Usernames and Passwords

The PRECIS codec makes internationalized user names and passwords safer for use by applications. 
PRECIS profiles transform unicode strings into a canonical form, suitable for byte-by-byte comparison.

This module implements the PRECIS Framework as described in:

- PRECIS Framework: Preparation, Enforcement, and Comparison of Internationalized Strings in Application Protocols (RFC 7564)
- Preparation, Enforcement, and Comparison of Internationalized Strings Representing Usernames and Passwords (RFC 7613)
- Preparation, Enforcement, and Comparison of Internationalized Strings Representing Nicknames (RFC 7700)

## Supported Codecs

- UsernamePreserved
- UsernameCaseMapped
- OpaqueString
- NicknamePreserved
- NicknameCaseMapped

## Usage

Import the `precis_codec` module to register the codec names. You can then `encode` any unicode string. `encode` will raise a `UnicodeEncodeError` if the string is disallowed.

```python
>>> import precis_codec
>>> 'Kevin'.encode('UsernamePreserved')
b'Kevin'
>>> '\u212Aevin'.encode('UsernamePreserved')
b'Kevin'
>>> '\uFF2Bevin'.encode('UsernamePreserved')
b'Kevin'
>>> '\u212Aevin'.encode('UsernameCaseMapped')
b'kevin'
>>> '\uFF2Bevin'.encode('OpaqueString')
b'\xef\xbc\xabevin'
>>> '\U0001F17Aevin'.encode('UsernamePreserved')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  ...
  File "precis_codec/baseclass.py", line 29, in _enforce
    '%s/%s' % (prop, kind))
UnicodeEncodeError: 'usernamepreserved' codec can't encode character 'U0001f17a' in position 0: FREE_PVAL/symbols
```

## Examples

There are multiple ways to write "Kevin" by varying only the "K".

Original String|UsernamePreserved|UsernameCaseMapped
---------------|-----------------|------------------
Kevin | Kevin | kevin
&#x212A;evin '\u212Aevin' | Kevin | kevin
&#xFF2B;evin '\uFF2Bevin' | Kevin | kevin
&#x039A;evin '\u039Aevin' | &#x039A;evin '\u039Aevin' | &#x03BA;evin '\u03BAevin'
&#x1e32;evin '\u1E32evin' | &#x1e32;evin '\u1E32evin' | &#x1E33;evin '\u1E33evin'
&#x1E34;evin '\u1E34evin' | &#x1E34;evin '\u1E34evin' | &#x1E35;evin '\u1E35evin'
&#x2c69;evin '\u2C69evin' | &#x2c69;evin '\u2C69evin' | &#x2C6A;evin '\u2C6Aevin'
&#xA740;evin '\uA740evin' | &#xA740;evin '\uA740evin' | &#xA741;evin '\uA741evin'
&#xA742;evin '\uA742evin' | &#xA742;evin '\uA742evin' | &#xA743;evin '\uA743evin'
&#xA744;evin '\uA744evin' | &#xA744;evin '\uA744evin' | &#xA745;evin '\uA745evin'
&#xA7A2;evin '\uA7A2evin' | &#xA7A2;evin '\uA7A2evin' | &#xA7A3;evin '\uA7A3evin'
&#x24C0;evin '\u24C0evin'  | DISALLOWED | DISALLOWED
&#x1F11A;evin '\U0001F11Aevin' | DISALLOWED | DISALLOWED
&#x1F13A;evin '\U0001F13Aevin' | DISALLOWED | DISALLOWED
&#x1F15A;evin '\U0001F15Aevin' | DISALLOWED | DISALLOWED
&#x1F17A;evin '\U0001F17Aevin' | DISALLOWED | DISALLOWED
