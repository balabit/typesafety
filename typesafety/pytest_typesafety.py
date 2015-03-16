


def pytest_addoption(parser):
    parser.addoption(
        '-T', '--enable-typesafety', action='append', metavar='MODULE',
        help='Enable typesafety for the given modules'
    )


def pytest_configure(config):
    if config.getoption('enable_typesafety'):
        import typesafety
        import functools

        enabled_for = tuple(
            mod.split('.') for mod in config.getoption('enable_typesafety')
        )
        filter_func = functools.partial(__check_need_activate,
                                        enabled_for=enabled_for)
        typesafety.activate(filter_func=filter_func)


def __check_need_activate(module_name, enabled_for):
    module_name = module_name.split('.')
    return any(
        module_name[:len(name)] == name for name in enabled_for
    )
