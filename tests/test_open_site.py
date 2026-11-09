from selenium import webdriver

from config import BASE_URL


def test_open_site(driver):
    driver.get(f"{BASE_URL}/home")

    assert "Alps Jobs" in driver.title, (
        f"Unexpected page title: {driver.title!r}"
    )
    assert driver.find_element("tag name", "body").is_displayed()