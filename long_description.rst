PRECIS Codec: Internationalized Usernames and Passwords
=======================================================

|Build Status| |codecov.io|

The PRECIS codec makes internationalized user names and passwords safer
for use by applications. PRECIS profiles transform unicode strings into
a canonical UTF-8 form, suitable for byte-by-byte comparison.

This module implements the PRECIS Framework as described in:

-  PRECIS Framework: Preparation, Enforcement, and Comparison of
   Internationalized Strings in Application Protocols (RFC 7564)
-  Preparation, Enforcement, and Comparison of Internationalized Strings
   Representing Usernames and Passwords (RFC 7613)
-  Preparation, Enforcement, and Comparison of Internationalized Strings
   Representing Nicknames (RFC 7700)

Supported Codecs
----------------

Each PRECIS profile has a corresponding codec name. The ``CaseMapped``
variant converts the string to lower case for implementing
case-insensitive comparison.

-  UsernameCasePreserved
-  UsernameCaseMapped
-  Nickname
-  OpaqueString

Usage
-----

Import the ``precis_codec`` module to register the PRECIS codec names.
Use the ``encode`` method with any unicode string. ``encode`` will raise
a ``UnicodeEncodeError`` if the string is disallowed.

.. code:: python

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
      File "<stdin>", line 1, in <module>
      ...
      File "precis_codec/baseclass.py", line 29, in _enforce
        '%s/%s' % (prop, kind))
    UnicodeEncodeError: 'usernamecasepreserved' codec can't encode character 'U0001f17a' in position 0: FREE_PVAL/symbols

.. |Build Status| image:: https://travis-ci.org/byllyfish/precis_codec.svg?branch=master
   :target: https://travis-ci.org/byllyfish/precis_codec
.. |codecov.io| image:: https://codecov.io/gh/byllyfish/precis_codec/coverage.svg?branch=master
   :target: https://codecov.io/gh/byllyfish/precis_codec?branch=master
