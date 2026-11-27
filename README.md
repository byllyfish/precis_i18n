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

Requires Python 3.7 or later.

## Usage

Use the `get_profile` function to obtain a profile object, then use its
`enforce` method. The `enforce` method returns a Unicode string.

```pycon
>>> from precis_i18n import get_profile
>>> username = get_profile('UsernameCaseMapped')
>>> username.enforce('Kevin')
'kevin'
>>> username.enforce('\u212Aevin')
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'UsernameCaseMapped' codec can't encode character '\u212a' in position 0: DISALLOWED/has_compat
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
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'UsernameCasePreserved' codec can't encode character '\u212a' in position 0: DISALLOWED/has_compat
>>> '\uFF2Bevin'.encode('UsernameCasePreserved')
b'Kevin'
>>> '\u212Aevin'.encode('UsernameCaseMapped')
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'UsernameCaseMapped' codec can't encode character '\u212a' in position 0: DISALLOWED/has_compat
>>> '\uFF2Bevin'.encode('OpaqueString')
b'\xef\xbc\xabevin'
>>> '\U0001F17Aevin'.encode('UsernameCasePreserved')
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'UsernameCasePreserved' codec can't encode character '\U0001f17a' in position 0: DISALLOWED/symbols

```

## Unicode configurations

The default uses the interpreter's Unicode categories, combining classes,
directionality, normalization and casing with the current bundled supplementary
properties. The existing `unicodedata=` argument accepts an alternate
database. Without an explicit version selection, that legacy alternate mode
continues to use interpreter-native lowercase and casefold.

Select `unicode_version="17.0.0"` or `unicode_version="18.0.0"` to use
matching bundled width, case-mapping and contextual data. The selected
database must report the same Unicode version and provide category,
normalization, combining class and bidi operations. Versioned setup rejects
providers that fail a canonical reordering check. Omit the provider when
the interpreter's built-in database matches. Applications can separately
install a matching `unicodedata2` version and pass it as the provider.
The package does not install that provider.

```python
import unicodedata2

from precis_i18n import get_profile, get_profile_identity

username = get_profile(
    "UsernameCaseMapped", unicodedata=unicodedata2, unicode_version="18.0.0"
)
identity = get_profile_identity(username)
key = username.comparison_key("Kevin")
```

Application-supplied database objects can declare a stable
`precis_data_identity` string covering their actual implementation and data.
They must keep the declared data and behavior fixed. Legacy external
providers without an identity still work and expose a descriptor with no
attestable fingerprint. The descriptor includes the profile, standards
generation, case rules, normalization, Unicode versions, data identity and
execution mode. For built-in databases and identified `unicodedata2`
distributions, it also records the runtime and platform. Compare equivalent
configurations across runtimes using independent conformance evidence. A
provider or profile change can alter admission or create key collisions.
Revalidate the identity domain before changing the active policy.

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

The bare string classes return exact comparison octets after class admission.

For RFC 8266 nickname display, use `NicknameCasePreserved.enforce()`.
Its `comparison_key()` applies the profile's lowercase comparison mapping
and returns exact UTF-8 bytes. `Nickname` remains an alias for the historical
lowercase-enforcement variant. The explicit casefold variants implement a
different equality policy. Compute the comparison key from the original
nickname. The RFC applies lowercase before NFKC for comparison, while
display enforcement preserves case. For example, U+2100 followed by
capital sigma produces a different key if display normalization precedes
comparison. Compare keys under the same profile and data identity. Treat plaintext and prepared credentials as sensitive, including
the input object carried by Python's `UnicodeEncodeError`.

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

## Unicode version updates

- Add the new official UCD inputs and SHA-256 digests to
  `tools/unicode_sources.json`. The generator verifies each file before
  using it. Keep the Unicode data notice with the derived tables.
- Run `nox -s unicode_data -- /path/to/ucd-parent /path/to/output`.
  Compare the generated package data and retain the existing supported
  generation unless its removal is an intentional compatibility change.
- Audit derived-property differences against the authoritative files. Update
  the code-point fixture only for reviewed changes.
- Run the complete source and installed-wheel Nox suites. With a local
  provider lock and wheelhouse, run `unicode_source` and `unicode_wheel`
  for each selected generation and supported interpreter.

Set `PRECIS_QUALIFICATION_DIR` to an external directory for JUnit and
build artifacts. `PRECIS_PROVIDER_LOCK` and `PRECIS_PROVIDER_WHEELHOUSE`
select optional test artifacts by their exact hashes. The library has
no mandatory runtime dependencies.

Use `nox --default-venv-backend venv` when the installed virtualenv seeder
no longer supplies pip for an older target interpreter.
