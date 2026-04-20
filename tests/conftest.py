import pytest
import shutil
import time

@pytest.fixture(autouse=True)
def cleanup_teardown():
    yield
    time.sleep(0.5)