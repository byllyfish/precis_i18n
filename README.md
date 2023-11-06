# PRECIS-i18n: Internationalized Usernames and Passwords

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/byllyfish/precis_i18n/main/LICENSE.txt)
[![Build Status](https://github.com/byllyfish/precis_i18n/actions/workflows/ci.yml/badge.svg)](https://github.com/byllyfish/precis_i18n/actions/workflows/ci.yml)
[![codecov.io](https://codecov.io/gh/byllyfish/precis_i18n/coverage.svg?branch=main)](https://codecov.io/gh/byllyfish/precis_i18n?branch=main)

If you want your application to accept Unicode user names and passwords,
you must be careful in how you validate and compare them. The PRECIS
framework makes internationalized user names and passwords safer for use
by applications. PRECIS profiles transform Unicode strings into a
canonical form, suitable for comparison.

This module implements the PRECIS Framework as described in:

-   PRECIS Framework: Preparation, Enforcement, and Comparison of
    Internationalized Strings in Application Protocols ([RFC
    8264](https://tools.ietf.org/html/rfc8264))
-   Preparation, Enforcement, and Comparison of Internationalized
    Strings Representing Usernames and Passwords ([RFC
    8265](https://tools.ietf.org/html/rfc8265))
-   Preparation, Enforcement, and Comparison of Internationalized
    Strings Representing Nicknames ([RFC
    8266](https://tools.ietf.org/html/rfc8266))

Requires Python 3.5 or later.

## Usage

Use the `get_profile` function to obtain a profile object, then use its
`enforce` method. The `enforce` method returns a Unicode string.

```pycon
>>> from precis_i18n import get_profile
>>> username = get_profile('UsernameCaseMapped')
>>> username.enforce('Kevin')
'kevin'
>>> username.enforce('\u212Aevin')
'kevin'
>>> username.enforce('\uFF2Bevin')
'kevin'
>>> username.enforce('\U0001F17Aevin')
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'UsernameCaseMapped' codec can't encode character '\U0001f17a' in position 0: DISALLOWED/symbols

```

Alternatively, you can use the Python `str.encode` API. Import the
`precis_i18n.codec` module to register the PRECIS codec names. Now you
can use the `str.encode` method with any Unicode string. The result will
be a UTF-8 encoded byte string or a `UnicodeEncodeError` if the string
is disallowed.

```pycon
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
UnicodeEncodeError: 'UsernameCasePreserved' codec can't encode character '\U0001f17a' in position 0: DISALLOWED/symbols

```

## Alternative Unicode Versions

The `get_profile` function uses whatever version of `unicodedata` is
provided by the Python runtime. The Unicode version is usually tied to
the major version of the Python runtime. Python 3.7.x uses Unicode 11.0.
Python 3.6.x uses Unicode 10.0.

To use an alternative `unicodedata` implementation, pass the
`unicodedata` keyword argument to `get_profile`.

For example, you could separately install version 12.0 of the
`unicodedata2` module from PyPI. Then, pass it to get_profile to
retrieve a profile that uses Unicode 12.0.

```pycon
>>> import unicodedata2
>>> from precis_i18n import get_profile
>>> username = get_profile('UsernameCaseMapped', unicodedata=unicodedata2)
>>> username.enforce('Kevin')
'kevin'

```

## Supported Profiles and Codecs

Each PRECIS profile has a corresponding codec name. The `CaseMapped`
variant converts the string to lower case for implementing
case-insensitive comparison.

-   UsernameCasePreserved
-   UsernameCaseMapped
-   OpaqueString
-   NicknameCasePreserved
-   NicknameCaseMapped

The `CaseMapped` profiles use Unicode `ToLower` per the latest RFC.
Previous versions of this package used Unicode Default Case Folding.
There are CaseMapped variants for different case transformations. These
profile names are deprecated:

-   UsernameCaseMapped:ToLower
-   UsernameCaseMapped:CaseFold
-   NicknameCaseMapped:ToLower
-   NicknameCaseMapped:CaseFold

The PRECIS base string classes are also available as codecs:

-   IdentifierClass
-   FreeFormClass

## Userparts and Space Delimited Usernames

The Username profiles in this implementation do not allow spaces. The
Username profiles correspond to the definition of \"userparts\" in RFC
8265. If you want to allow spaces in your application\'s user names, you
must split the string first.

```python
def enforce_app_username(name):
    profile = precis_i18n.get_profile('UsernameCasePreserved')
    userparts = [profile.enforce(userpart) for userpart in name.split(' ')]
    return ' '.join(userparts)
```

Be aware that a username constructed this way can contain bidirectional
text in the separate userparts.

## Error Messages

A PRECIS profile raises a `UnicodeEncodeError` exception if a string is
disallowed. The `reason` field specifies the kind of error.

Reason                                 | Explanation
-------------------------------------- | ------------------------------------------
DISALLOWED/arabic_indic                |  Arabic-Indic digits cannot be mixed with Extended Arabic-Indic Digits. (Context)
DISALLOWED/bidi_rule                   |  Right-to-left string cannot contain left-to-right characters due to the \"Bidi\" rule. (Context)
DISALLOWED/controls                    |  Control character is not allowed.
DISALLOWED/empty                       |  After applying the profile, the result cannot be empty.
DISALLOWED/exceptions                  |  Exception character is not allowed.
DISALLOWED/extended_arabic_indic       |    Extended Arabic-Indic digits cannot be mixed with Arabic-Indic Digits. (Context)
DISALLOWED/greek_keraia                |    Greek keraia must be followed by a Greek character. (Context)
DISALLOWED/has_compat                  |    Compatibility characters are not allowed.
DISALLOWED/hebrew_punctuation          |    Hebrew punctuation geresh or gershayim must be preceded by Hebrew character. (Context)
DISALLOWED/katakana_middle_dot         |    Katakana middle dot must be accompanied by a Hiragana, Katakana, or Han character. (Context)
DISALLOWED/middle_dot                  |    Middle dot must be surrounded by the letter \'l\'. (Context)
DISALLOWED/not_idempotent              |    After reapplying the profile, the result is not stable.
DISALLOWED/old_hangul_jamo             |    Conjoining Hangul Jamo is not allowed.
DISALLOWED/other                       |    Other character is not allowed.
DISALLOWED/other_letter_digits         |    Non-traditional letter or digit is not allowed.
DISALLOWED/precis_ignorable_properties | Default ignorable or non-character is not allowed.
DISALLOWED/punctuation                 |   Non-ASCII punctuation character is not allowed.
DISALLOWED/spaces                      |   Space character is not allowed.
DISALLOWED/symbols                     |   Non-ASCII symbol character is not allowed.
DISALLOWED/unassigned                  |   Unassigned Unicode character is not allowed.
DISALLOWED/zero_width_joiner           |   Zero width joiner must immediately follow a combining virama. (Context)
DISALLOWED/zero_width_nonjoiner        |   Zero width non-joiner must immediately follow a combining virama, or appear where it breaks a cursive connection in a formally cursive script. (Context)


## The Nickname Profile and White Space

When PRECIS processes a string using the `Nickname` profile, one of the
enforcement steps silently removes leading and trailing white space.
Starting with version 1.1, this library uses a more *restrictive*
definition of *white space* in the `Nickname` profile.

-   1.1 and later *only* include Unicode category `Zs`. If you try to
    enforce a Nickname that contains white space characters like `'\n'`,
    you will get a UnicodeEncodeError `DISALLOWED/controls`.
-   1.0.5 and earlier included control characters such as `'\n'`,
    `'\t'`, and `'\r'` when removing leading/trailing white space from
    Nicknames. The result treated these legacy white space characters
    the same as `Zs` and stripped them.
-   In all versions, *internal* white space (not leading or trailing)
    matches Unicode category `Zs` only.

The trimming of white space is specific to the Nickname profile only.
Here is an example of the current behavior:

```pycon
>>> from precis_i18n import get_profile
>>> nickname = get_profile('NicknameCaseMapped')
>>> nickname.enforce('Kevin\n')
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'NicknameCaseMapped' codec can't encode character '\x0a' in position 5: DISALLOWED/controls

```

In version 1.0.5 and earlier, the `NicknameCaseMapped` profile enforced `"Kevin\n"`
as `"kevin"`.

## Unicode Version Update Procedure

When Unicode releases a new version, take the following steps to update
internal tables and pass unit tests:

-   Under a version of Python that supports the new Unicode version, run
    the tests using `python -m unittest discover` and check that the
    `test_derived_props` test FAILS due to a missing file.
-   Generate a new `derived-props` file by running
    `PYTHONPATH=. python test/test_derived_props.py > derived-props-VERSION.txt`.
    Rename the file using the Unicode version, and re-run the tests. The
    unit tests will further check that no derived properties in the new
    file contradict the previous values.
-   Check for changes to internal tables used for context rules by
    running `PYTHONPATH=. python tools/check_codepoints.py`. Update the
    corresponding tables in precis_i18n/unicode.py if necessary.
