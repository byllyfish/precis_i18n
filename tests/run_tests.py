import precis_codec


def _escape(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return s.encode('unicode-escape').decode('ascii')


def _unescape(s):
    return s.encode('raw-unicode-escape').decode('unicode_escape')


def allow(cmd, codec_name):
    print('ALLOW', _escape(cmd[0]), cmd[0])
    source = cmd[0]
    expected = cmd[1] if len(cmd) > 1 else source
    actual = source.encode(codec_name)
    # Compare actual to expected value.
    if actual != expected.encode('utf-8'):
        print(_escape(actual))
        raise ValueError('ALLOW: expected %s but got %s' % (expected, actual))
    # Make sure encoding is idempotent.
    if actual != actual.decode('utf-8').encode(codec_name):
        raise ValueError('ALLOW: Idempotent test failed')


def disallow(cmd, codec_name):
    print('DISALLOW', _escape(cmd[0]), cmd[0])
    source = cmd[0]
    error = cmd[1] if len(cmd) > 1 else '<error field missing>'
    try:
        source.encode(codec_name)
    except UnicodeEncodeError as ex:
        if error not in ex.reason:
            raise ValueError(
                'DISALLOW: Unexpected error: expected "%s" but got "%s"' %
                (error, ex.reason))
        return
    raise ValueError('DISALLOW: Value was allowed; expected failure')


def main():
    for line in open('precis_tests.txt', encoding='utf-8'):
        cmd = line.strip().split(maxsplit=2)
        if len(cmd) == 0:
            continue
        #print(cmd)
        cmd = [_unescape(s) for s in cmd]
        #print(cmd)

        if cmd[0] == 'PROFILE':
            codec_name = cmd[1]
        elif cmd[0] == 'ALLOW':
            allow(cmd[1:], codec_name)
        elif cmd[0] == 'DISALLOW':
            disallow(cmd[1:], codec_name)


if __name__ == '__main__':
    main()
