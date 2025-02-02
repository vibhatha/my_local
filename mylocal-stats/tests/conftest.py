import os
import django
import pytest

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    django.setup()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass 