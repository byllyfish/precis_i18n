Changelog
=========

0.6.0
-----

-  (IMPORTANT) This version changes the results of the Nickname profile.
-  Add support for proposed changes to RFC 7564 that will make the
   Nickname profile idempotent.
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
