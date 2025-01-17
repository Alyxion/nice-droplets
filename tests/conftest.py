import pytest
from selenium import webdriver

pytest_plugins = ['nicegui.testing.plugin']

@pytest.fixture
def chrome_options() -> webdriver.ChromeOptions:
    """Chrome options for headless testing."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    return options
