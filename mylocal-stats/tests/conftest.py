import os
import sys
import django
import pytest

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(__file__), '../src')
sys.path.insert(0, src_path)

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    django.setup()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(django_db_setup, db):
    """
    Enables database access for all tests
    """
    pass 