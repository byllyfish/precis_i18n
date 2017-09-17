PRECIS-i18n: Internationalized Usernames and Passwords
======================================================

|MIT licensed| |Build Status| |codecov.io|

If you want your application to accept unicode user names and passwords,
you must be careful in how you validate and compare them. The PRECIS
framework makes internationalized user names and passwords safer for use
by applications. PRECIS profiles transform unicode strings into a
canonical form, suitable for comparison.

This module implements the PRECIS Framework as described in:

-  PRECIS Framework: Preparation, Enforcement, and Comparison of
   Internationalized Strings in Application Protocols (`RFC
   7564 <https://tools.ietf.org/html/rfc7564>`__)
-  Preparation, Enforcement, and Comparison of Internationalized Strings
   Representing Usernames and Passwords (`RFC
   7613 <https://tools.ietf.org/html/rfc7613>`__)
-  Preparation, Enforcement, and Comparison of Internationalized Strings
   Representing Nicknames (`RFC
   7700 <https://tools.ietf.org/html/rfc7700>`__)

Requires Python 3.3 or later.

Usage
-----

Use the ``get_profile`` function to obtain a profile object, then use
its ``enforce`` method. The ``enforce`` method returns a Unicode string.

::


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

Alternatively, you can use the Python ``str.encode`` API. Import the
``precis_i18n.codec`` module to register the PRECIS codec names. Now you
can use the ``str.encode`` method with any unicode string. The result
will be a UTF-8 encoded byte string or a ``UnicodeEncodeError`` if the
string is disallowed.

::


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

Supported Profiles and Codecs
-----------------------------

Each PRECIS profile has a corresponding codec name. The ``CaseMapped``
variant converts the string to lower case for implementing
case-insensitive comparison.

-  UsernameCasePreserved
-  UsernameCaseMapped
-  OpaqueString
-  NicknameCasePreserved
-  NicknameCaseMapped

The ``CaseMapped`` profiles use Unicode Default Case Folding. There are
additional codecs that use Unicode ``ToLower`` to support draft RFC
changes.

-  UsernameCaseMapped:ToLower
-  NicknameCaseMapped:ToLower

The PRECIS base string classes are also available:

-  IdentifierClass
-  FreeFormClass

Error Messages
--------------

A PRECIS profile raises a ``UnicodeEncodeError`` exception if a string
is disallowed. The ``reason`` field specifies the kind of error.

+------------------------------+---------------------------------------------+
| Reason                       | Explanation                                 |
+==============================+=============================================+
| DISALLOWED/arabic\_indic     | Arabic-Indic digits cannot be mixed with    |
|                              | Extended Arabic-Indic Digits. (Context)     |
+------------------------------+---------------------------------------------+
| DISALLOWED/bidi\_rule        | Right-to-left string cannot contain         |
|                              | left-to-right characters due to the "Bidi"  |
|                              | rule. (Context)                             |
+------------------------------+---------------------------------------------+
| DISALLOWED/controls          | Control character is not allowed.           |
+------------------------------+---------------------------------------------+
| DISALLOWED/empty             | After applying the profile, the result      |
|                              | cannot be empty.                            |
+------------------------------+---------------------------------------------+
| DISALLOWED/exceptions        | Exception character is not allowed.         |
+------------------------------+---------------------------------------------+
| DISALLOWED/extended\_arabic\ | Extended Arabic-Indic digits cannot be      |
| _indic                       | mixed with Arabic-Indic Digits. (Context)   |
+------------------------------+---------------------------------------------+
| DISALLOWED/greek\_keraia     | Greek keraia must be followed by a Greek    |
|                              | character. (Context)                        |
+------------------------------+---------------------------------------------+
| DISALLOWED/has\_compat       | Compatibility characters are not allowed.   |
+------------------------------+---------------------------------------------+
| DISALLOWED/hebrew\_punctuati | Hebrew punctuation geresh or gershayim must |
| on                           | be preceded by Hebrew character. (Context)  |
+------------------------------+---------------------------------------------+
| DISALLOWED/katakana\_middle\ | Katakana middle dot must be accompanied by  |
| _dot                         | a Hiragana, Katakana, or Han character.     |
|                              | (Context)                                   |
+------------------------------+---------------------------------------------+
| DISALLOWED/middle\_dot       | Middle dot must be surrounded by the letter |
|                              | 'l'. (Context)                              |
+------------------------------+---------------------------------------------+
| DISALLOWED/not\_idempotent   | After reapplying the profile, the result is |
|                              | not stable.                                 |
+------------------------------+---------------------------------------------+
| DISALLOWED/old\_hangul\_jamo | Conjoining Hangul Jamo is not allowed.      |
+------------------------------+---------------------------------------------+
| DISALLOWED/other             | Other character is not allowed.             |
+------------------------------+---------------------------------------------+
| DISALLOWED/other\_letter\_di | Non-traditional letter or digit is not      |
| gits                         | allowed.                                    |
+------------------------------+---------------------------------------------+
| DISALLOWED/precis\_ignorable | Default ignorable or non-character is not   |
| \_properties                 | allowed.                                    |
+------------------------------+---------------------------------------------+
| DISALLOWED/punctuation       | Non-ASCII punctuation character is not      |
|                              | allowed.                                    |
+------------------------------+---------------------------------------------+
| DISALLOWED/spaces            | Space character is not allowed.             |
+------------------------------+---------------------------------------------+
| DISALLOWED/symbols           | Non-ASCII symbol character is not allowed.  |
+------------------------------+---------------------------------------------+
| DISALLOWED/unassigned        | Unassigned unicode character is not         |
|                              | allowed.                                    |
+------------------------------+---------------------------------------------+
| DISALLOWED/zero\_width\_join | Zero width joiner must immediately follow a |
| er                           | combining virama. (Context)                 |
+------------------------------+---------------------------------------------+
| DISALLOWED/zero\_width\_nonj | Zero width non-joiner must immediately      |
| oiner                        | follow a combining virama, or appear where  |
|                              | it breaks a cursive connection in a         |
|                              | formally cursive script. (Context)          |
+------------------------------+---------------------------------------------+

.. |MIT licensed| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/byllyfish/precis_i18n/master/LICENSE.txt
.. |Build Status| image:: https://travis-ci.org/byllyfish/precis_i18n.svg?branch=master
   :target: https://travis-ci.org/byllyfish/precis_i18n
.. |codecov.io| image:: https://codecov.io/gh/byllyfish/precis_i18n/coverage.svg?branch=master
   :target: https://codecov.io/gh/byllyfish/precis_i18n?branch=master
