= PRECIS Codec

The PRECIS codec makes i18n user names and passwords safer for use by applications. 
PRECIS profiles transform strings into a canonical form, suitable for comparison.

This module implements the PRECIS Framework as described in:

- PRECIS Framework: Preparation, Enforcement, and Comparison of Internationalized Strings in Application Protocols (RFC 7564)
- Preparation, Enforcement, and Comparison of Internationalized Strings Representing Usernames and Passwords (RFC 7613)
- Preparation, Enforcement, and Comparison of Internationalized Strings Representing Nicknames (RFC 7700)

Examples:

UsernamePreserved

'Kevin'       ->  'Kevin'
'\u212Aevin'  ->  'Kevin'
'\uFF2Bevin'  ->  'Kevin'
'\u039Aevin'  ->  '\u039Aevin'
'\u1E32evin'  ->  '\u1E32evin'
'\u1E34evin'  ->  '\u1E34evin'
'\u2C69evin'  ->  '\u2C69evin'
'\uA740evin'  ->  '\uA740evin'
'\uA742evin'  ->  '\uA742evin'
'\uA744evin'  ->  '\uA744evin'
'\uA7A2evin'  ->  '\uA7A2evin'
'\u24C0evin'  ->   DISALLOW
'\U000E004B'  ->   DISALLOW
'\U0001F11A'  ->   DISALLOW
'\U0001F13A'  ->   DISALLOW
'\U0001F15A'  ->   DISALLOW
'\U0001F17A'  ->   DISALLOW

== Usage

import precis_codec

'\u212Aevin'.encode('UsernamePreserved')


== Supported Codecs

- UsernamePreserved
- UsernameCaseMapped
- OpaqueString
- NicknamePreserved
- NicknameCaseMapped

