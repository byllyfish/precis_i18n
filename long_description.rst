PRECIS Codec: Internationalized Usernames and Passwords
=======================================================

|MIT licensed| |Build Status| |codecov.io|

If you want your app to accept unicode user names and passwords, you
must be careful in how you compare them. The PRECIS codec makes
internationalized user names and passwords safer for use by
applications. PRECIS profiles transform unicode strings into a canonical
UTF-8 form, suitable for byte-by-byte comparison.

This module implements the PRECIS Framework as described in:

-  PRECIS Framework: Preparation, Enforcement, and Comparison of
   Internationalized Strings in Application Protocols (RFC 7564)
-  Preparation, Enforcement, and Comparison of Internationalized Strings
   Representing Usernames and Passwords (RFC 7613)
-  Preparation, Enforcement, and Comparison of Internationalized Strings
   Representing Nicknames (RFC 7700)

Usage
-----

Import the ``precis_codec.codec`` module to register the PRECIS codec
names. Use the ``encode`` method with any unicode string. ``encode``
will raise a ``UnicodeEncodeError`` if the string is disallowed.

::


    >>> import precis_codec.codec
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


    >>> from precis_codec import usernamecasemapped as username
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

Supported Codecs
----------------

Each PRECIS profile has a corresponding codec name. The ``casemapped``
variant converts the string to lower case for implementing
case-insensitive comparison.

-  usernamecasepreserved
-  usernamecasemapped
-  nickname
-  opaquestring

Examples
--------

There are multiple ways to write "Kevin" by varying only the "K".

+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Original String                       | UsernameCasePreserved             | UsernameCaseMapped                | Nickname                              |
+=======================================+===================================+===================================+=======================================+
| Kevin                                 | Kevin                             | kevin                             | kevin                                 |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Kevin ':raw-latex:`\u2`12Aevin'       | Kevin                             | kevin                             | kevin                                 |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ｋevin ':raw-latex:`\uFF`2Bevin'      | Kevin                             | kevin                             | kevin                                 |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Κevin ':raw-latex:`\u0`39Aevin'       | Κevin ':raw-latex:`\u0`39Aevin'   | κevin ':raw-latex:`\u0`3BAevin'   | κevin ':raw-latex:`\u0`3BAevin'       |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ḳevin ':raw-latex:`\u1`E32evin'       | Ḳevin ':raw-latex:`\u1`E32evin'   | ḳevin ':raw-latex:`\u1`E33evin'   | ḳevin ':raw-latex:`\u1`E33evin'       |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ḵevin ':raw-latex:`\u1`E34evin'       | Ḵevin ':raw-latex:`\u1`E34evin'   | ḵevin ':raw-latex:`\u1`E35evin'   | ḵevin ':raw-latex:`\u1`E35evin'       |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ⱪevin ':raw-latex:`\u2`C69evin'       | Ⱪevin ':raw-latex:`\u2`C69evin'   | ⱪevin ':raw-latex:`\u2`C6Aevin'   | ⱪevin ':raw-latex:`\u2`C6Aevin'       |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ꝁevin ':raw-latex:`\uA`740evin'       | Ꝁevin ':raw-latex:`\uA`740evin'   | ꝁevin ':raw-latex:`\uA`741evin'   | ꝁevin ':raw-latex:`\uA`741evin'       |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ꝃevin ':raw-latex:`\uA`742evin'       | Ꝃevin ':raw-latex:`\uA`742evin'   | ꝃevin ':raw-latex:`\uA`743evin'   | ꝃevin ':raw-latex:`\uA`743evin'       |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ꝅevin ':raw-latex:`\uA`744evin'       | Ꝅevin ':raw-latex:`\uA`744evin'   | ꝅevin ':raw-latex:`\uA`745evin'   | ꝅevin ':raw-latex:`\uA`745evin'       |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ꞣevin ':raw-latex:`\uA`7A2evin'       | Ꞣevin ':raw-latex:`\uA`7A2evin'   | ꞣevin ':raw-latex:`\uA`7A3evin'   | ꞣevin ':raw-latex:`\uA`7A3evin'       |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| Ⓚevin ':raw-latex:`\u2`4C0evin'       | DISALLOWED                        | DISALLOWED                        | kevin                                 |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| 🄚evin ':raw-latex:`\U`0001F11Aevin'   | DISALLOWED                        | DISALLOWED                        | (K)evin                               |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| 🄺evin ':raw-latex:`\U`0001F13Aevin'   | DISALLOWED                        | DISALLOWED                        | Kevin                                 |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| 🅚evin ':raw-latex:`\U`0001F15Aevin'   | DISALLOWED                        | DISALLOWED                        | 🅚evin ':raw-latex:`\U`0001F15Aevin'   |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+
| 🅺evin ':raw-latex:`\U`0001F17Aevin'   | DISALLOWED                        | DISALLOWED                        | 🅺evin ':raw-latex:`\U`0001F17Aevin'   |
+---------------------------------------+-----------------------------------+-----------------------------------+---------------------------------------+

.. |MIT licensed| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/byllyfish/precis_codec/master/LICENSE.txt
.. |Build Status| image:: https://travis-ci.org/byllyfish/precis_codec.svg?branch=master
   :target: https://travis-ci.org/byllyfish/precis_codec
.. |codecov.io| image:: https://codecov.io/gh/byllyfish/precis_codec/coverage.svg?branch=master
   :target: https://codecov.io/gh/byllyfish/precis_codec?branch=master
