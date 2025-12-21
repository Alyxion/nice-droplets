import pytest
from selenium import webdriver

@pytest.fixture
def chrome_options() -> webdriver.ChromeOptions:
    """Chrome options for the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    return options
