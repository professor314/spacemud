"""
pytest configuration for the Space MUD test suite.

Configures Django/Evennia and creates the test database before any
Evennia-dependent tests run.
"""

import os
import pytest


def pytest_configure(config):
    """Called before test collection. Set up Django and Evennia globals."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")

    import django
    try:
        django.setup()
    except RuntimeError:
        pass

    # Evennia._init() populates SESSION_HANDLER and other global singletons
    # that EvenniaTest.setUp() depends on.
    try:
        import evennia
        evennia._init()
    except Exception:
        pass

    # Set up the Django test environment (disables email sending, etc.)
    from django.test.utils import setup_test_environment
    try:
        setup_test_environment()
    except RuntimeError:
        # Already set up.
        pass

    # Tell Evennia's object manager we're in a test environment so it
    # gracefully handles missing DEFAULT_HOME objects.
    from django.conf import settings as django_settings
    django_settings.TEST_ENVIRONMENT = True


@pytest.fixture(scope="session", autouse=True)
def django_test_db(request):
    """
    Session-scoped fixture that creates the Django test database once for the
    entire test session and tears it down afterwards.

    This is needed because EvenniaTest (a django.test.TestCase subclass) uses
    database transactions and requires the test DB tables to exist.
    """
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=0)
    old_config = runner.setup_databases()
    yield
    runner.teardown_databases(old_config)
