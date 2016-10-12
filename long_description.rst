PRECIS-i18n: Internationalized Usernames and Passwords
======================================================

|MIT licensed| |Build Status| |codecov.io|

If you want your application to accept unicode user names and passwords,
you must be careful in how you validate and compare them. The PRECIS
framework makes internationalized user names and passwords safer for use
by applications. PRECIS profiles transform unicode strings into a
canonical UTF-8 form, suitable for byte-by-byte comparison.

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

Import the ``precis_i18n.codec`` module to register the PRECIS codec
names. Use the ``encode`` method with any unicode string. ``encode``
will raise a ``UnicodeEncodeError`` if the string is disallowed.

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
    UnicodeEncodeError: 'UsernameCasePreserved' codec can't encode character '\U0001f17a' in position 0: FREE_PVAL/symbols

Alternatively, you can use a PRECIS profile directly, without installing
a codec.

::


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

.. |MIT licensed| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/byllyfish/precis_i18n/master/LICENSE.txt
.. |Build Status| image:: https://travis-ci.org/byllyfish/precis_i18n.svg?branch=master
   :target: https://travis-ci.org/byllyfish/precis_i18n
.. |codecov.io| image:: https://codecov.io/gh/byllyfish/precis_i18n/coverage.svg?branch=master
   :target: https://codecov.io/gh/byllyfish/precis_i18n?branch=master
