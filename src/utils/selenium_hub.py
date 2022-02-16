"""Selenium Utils."""

import sys
from time import sleep

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def get_web_driver(url: str, hub: str = "http://selenium-hub:4444/wd/hub", browser: str = "FIREFOX",
                   wait_until_id: list = [By.ID, "__next"]):
    """Returns web driver."""
    desired_capabilities = DesiredCapabilities.CHROME.copy() if browser == "CHROME" else \
        DesiredCapabilities.FIREFOX.copy()
    desired_capabilities["marionette"] = False
    page_html = BeautifulSoup('', 'html5lib')
    try:
        with webdriver.Remote(
                command_executor=hub,
                desired_capabilities=desired_capabilities
        ) as driver:
            try:
                driver.get(url)
                sleep(1)
                page_html = BeautifulSoup(
                    WebDriverWait(driver, 10).until(lambda d: d.find_element(wait_until_id[0], wait_until_id[1]))
                        .get_attribute('innerHTML'),
                    'html5lib'
                )
            except TimeoutException:
                print(f"Element {wait_until_id[1]} not found", file=sys.stdout)
            finally:
                return page_html

    except SessionNotCreatedException:
        print('Could not start a new session', file=sys.stdout)
        return page_html
