# PRECIS-i18n: Internationalized Usernames and Passwords

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/byllyfish/precis_i18n/master/LICENSE.txt) [![Build Status](https://travis-ci.org/byllyfish/precis_i18n.svg?branch=master)](https://travis-ci.org/byllyfish/precis_i18n) [![codecov.io](https://codecov.io/gh/byllyfish/precis_i18n/coverage.svg?branch=master)](https://codecov.io/gh/byllyfish/precis_i18n?branch=master)

If you want your application to accept unicode user names and passwords, you must be careful in how you validate and compare them. The PRECIS framework makes internationalized user names and passwords safer for use by applications. PRECIS profiles transform unicode strings into a canonical UTF-8 form, suitable for byte-by-byte comparison.

This module implements the PRECIS Framework as described in:

- PRECIS Framework: Preparation, Enforcement, and Comparison of Internationalized Strings in Application Protocols ([RFC 7564](https://tools.ietf.org/html/rfc7564))
- Preparation, Enforcement, and Comparison of Internationalized Strings Representing Usernames and Passwords ([RFC 7613](https://tools.ietf.org/html/rfc7613))
- Preparation, Enforcement, and Comparison of Internationalized Strings Representing Nicknames ([RFC 7700](https://tools.ietf.org/html/rfc7700))

Requires Python 3.3 or later.

## Usage

Import the `precis_i18n.codec` module to register the PRECIS codec names. Use the `encode` method with any unicode string. `encode` will raise a `UnicodeEncodeError` if the string is disallowed.

```

>>> import precis_i18n.codec
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
UnicodeEncodeError: 'UsernameCasePreserved' codec can't encode character '\U0001f17a' in position 0: FREE_PVAL/symbols

```

Alternatively, you can use a PRECIS profile directly, without installing a codec.

```

>>> from precis_i18n import get_profile
>>> username = get_profile('UsernameCaseMapped')
>>> username.enforce('Kevin')
b'kevin'
>>> username.enforce('\u212Aevin')
b'kevin'
>>> username.enforce('\uFF2Bevin')
b'kevin'
>>> username.enforce('\U0001F17Aevin')
Traceback (most recent call last):
    ...
UnicodeEncodeError: 'UsernameCaseMapped' codec can't encode character '\U0001f17a' in position 0: FREE_PVAL/symbols

```

## Supported Profiles and Codecs

Each PRECIS profile has a corresponding codec name. The `CaseMapped` variant converts the string to lower case for implementing case-insensitive comparison.

- UsernameCasePreserved
- UsernameCaseMapped
- OpaqueString
- NicknameCasePreserved
- NicknameCaseMapped

The `CaseMapped` profiles use Unicode Default Case Folding. There are additional codecs that use Unicode `ToLower` to support draft RFC changes.

- UsernameCaseMapped:ToLower
- NicknameCaseMapped:ToLower

The PRECIS base string classes are also available:

- IdentifierClass
- FreeFormClass

## Examples

There are multiple ways to write "Kevin" by varying only the "K".

Original String|UsernameCasePreserved|UsernameCaseMapped|Nickname
---------------|-----------------|------------------|------------------
Kevin | Kevin | kevin | kevin
&#8490;evin '\u212aevin' | Kevin | kevin | kevin
&#65323;evin '\uff2bevin' | Kevin | kevin | kevin
&#922;evin '\u039aevin' | &#922;evin '\u039aevin' | &#954;evin '\u03baevin' | &#954;evin '\u03baevin'
&#7730;evin '\u1e32evin' | &#7730;evin '\u1e32evin' | &#7731;evin '\u1e33evin' | &#7731;evin '\u1e33evin'
&#7732;evin '\u1e34evin' | &#7732;evin '\u1e34evin' | &#7733;evin '\u1e35evin' | &#7733;evin '\u1e35evin'
&#11369;evin '\u2c69evin' | &#11369;evin '\u2c69evin' | &#11370;evin '\u2c6aevin' | &#11370;evin '\u2c6aevin'
&#42816;evin '\ua740evin' | &#42816;evin '\ua740evin' | &#42817;evin '\ua741evin' | &#42817;evin '\ua741evin'
&#42818;evin '\ua742evin' | &#42818;evin '\ua742evin' | &#42819;evin '\ua743evin' | &#42819;evin '\ua743evin'
&#42820;evin '\ua744evin' | &#42820;evin '\ua744evin' | &#42821;evin '\ua745evin' | &#42821;evin '\ua745evin'
&#42914;evin '\ua7a2evin' | &#42914;evin '\ua7a2evin' | &#42915;evin '\ua7a3evin' | &#42915;evin '\ua7a3evin'
&#9408;evin '\u24c0evin' | DISALLOWED | DISALLOWED | kevin
&#127258;evin '\U0001f11aevin' | DISALLOWED | DISALLOWED | (K)evin
&#127290;evin '\U0001f13aevin' | DISALLOWED | DISALLOWED | Kevin
&#127322;evin '\U0001f15aevin' | DISALLOWED | DISALLOWED | &#127322;evin '\U0001f15aevin'
&#127354;evin '\U0001f17aevin' | DISALLOWED | DISALLOWED | &#127354;evin '\U0001f17aevin'
