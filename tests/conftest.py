import pytest
from selenium import webdriver

pytest_plugins = ['nicegui.testing.plugin']


@pytest.fixture
def chrome_options() -> webdriver.ChromeOptions:
    """Chrome options for headless testing."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    return options
