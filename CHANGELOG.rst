Changelog
=========

1.0.1
-----

- Fixed a dict/set syntax typo that has no runtime effect (6ae6876).
- Test forward compatibility of derived props test files as Unicode version increases.
- Test Unicode 11.0 (Python 3.7).
- Update copyright year (2019).

1.0.0
-----

-  Release 1.0 version.
-  Add test that all codepoints are idempotent.
-  Update copyright year (2018).

0.7.0
-----

-  (IMPORTANT) This version changes the results of the CaseMapped profiles due to publication of new RFC's.
-  The CaseMapped profiles now default to using ToLower instead of CaseFold.
-  Added profile variants for CaseFold, just for completeness.
-  Update references to RFC numbers in documentation and comments.

0.6.0
-----

-  (IMPORTANT) This version changes the results of the Nickname profile.
-  Add support for proposed changes to RFC 7564 that will make the
   Nickname profile idempotent (Issue #3).
-  Add the "DISALLOWED/not\_idempotent" error message.
-  Sign pypi package with gpg.

0.5.0
-----

-  (API CHANGE) Profile's ``enforce`` method now returns a Unicode
   string instead of UTF-8 bytes. This API change affects code that uses
   get\_profile() to obtain a profile. The codec still returns UTF-8
   bytes. (Issue 2)
-  The codec search function now returns None when it doesn't find a
   matching codec.

0.4.1
-----

-  Add LICENSE.txt and CHANGELOG.md to source tarball. (Issue 1)
-  Update travis and pypi metadata for Python 3.6.

0.4.0
-----

-  Improve error messages when a string is disallowed.
-  Clean up test examples. Add a few more test cases.

0.3.0
-----

-  Added the ``get_profile`` function to access profiles, when not using
   the codec.
-  Removed the global variables previously used to access profiles.
-  Added codecs for different case mappings of username and nickname.
-  Added codecs for base string classes: identifierclass and
   freeformclass.

0.2.2
-----

-  Initial release to PyPI.
