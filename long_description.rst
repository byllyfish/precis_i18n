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

Usage
-----

Import the ``precis_codec.codec`` module to register the PRECIS codec
names. Use the ``encode`` method with any unicode string. ``encode``
will raise a ``UnicodeEncodeError`` if the string is disallowed.

.. code:: python


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

.. code:: python


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

License
-------

MIT License

.. |Build Status| image:: https://travis-ci.org/byllyfish/precis_codec.svg?branch=master
   :target: https://travis-ci.org/byllyfish/precis_codec
.. |codecov.io| image:: https://codecov.io/gh/byllyfish/precis_codec/coverage.svg?branch=master
   :target: https://codecov.io/gh/byllyfish/precis_codec?branch=master
