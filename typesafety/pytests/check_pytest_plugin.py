import pytest

# pylint: disable=invalid-name
pytest_plugins = 'pytester'


@pytest.mark.parametrize('enabled', [True, False])
def test_enabled(testdir, enabled):
    testdir.makepyfile(
        identity='''
            def identity(i: int):
                return i
        ''',
        test_identity='''
            from identity import identity
            def test_identity():
                assert identity("name") == "name"
        ''')

    args = ['test_identity.py']
    if enabled:
        args = ['--enable-typesafety', 'identity'] + args
    result = testdir.runpytest(*args)

    expected = "*1 failed*" if enabled else "*1 passed*"
    result.stdout.fnmatch_lines([expected])
