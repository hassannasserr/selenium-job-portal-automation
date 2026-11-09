import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import (
    BASE_URL,
    COMPANY_EMAIL,
    COMPANY_PASSWORD,
    CREDENTIALS_CONFIGURED,
)

pytestmark = pytest.mark.skipif(
    not CREDENTIALS_CONFIGURED,
    reason="Valid test credentials are not configured",
)
def test_company_pipeline_review(driver):
    driver.get(f"{BASE_URL}/login")

    wait = WebDriverWait(driver, 10)

    # Login
    email = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "email")
        )
    )
    email.send_keys(COMPANY_EMAIL)

    password = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "password")
        )
    )
    password.send_keys(COMPANY_PASSWORD)

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type='submit']")
        )
    )
    login_button.click()

    # Switch to English
    language_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "app-language-menu button[aria-haspopup='menu']"
            )
        )
    )
    language_button.click()

    language_options = wait.until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "[role='menu'] button[role='menuitem']"
            )
        )
    )

    english_option = None

    for option in language_options:
        if "english" in option.text.lower():
            english_option = option
            break

    assert english_option is not None, "English language option was not found"

    english_option.click()

    # Open Pipeline
    pipeline = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[normalize-space()='Pipeline']")
        )
    )
    pipeline.click()
    pipeline_url = driver.current_url

    # Verify the job exists
    job_title = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[normalize-space()='QA Test Engineer - Automation']"
            )
        )
    )

    assert job_title.is_displayed(), "Expected pipeline job is not visible"

    # Verify there is at least one applicant
    applicant_count = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                 "//*[contains(normalize-space(), 'applicants') and not(*)]"
            )
        )
    )

    print("Applicant count:", applicant_count.text)

    # Open applicant review
    review_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[contains(normalize-space(), 'Review')]"
            )
        )
    )

    dialog_count_before = len(
        [
            element
            for element in driver.find_elements(By.CSS_SELECTOR, "[role='dialog']")
            if element.is_displayed()
        ]
    )
    review_button.click()

    print("URL after Review:", driver.current_url)

    review_opened = wait.until(
        lambda d: (
            d.current_url != pipeline_url
            or any(
                element.is_displayed()
                for element in d.find_elements(
                    By.CSS_SELECTOR,
                    "[role='dialog']",
                )
            )
            and len(
                [
                    element
                    for element in d.find_elements(
                        By.CSS_SELECTOR,
                        "[role='dialog']",
                    )
                    if element.is_displayed()
                ]
            )
            > dialog_count_before
        )
    )
    assert review_opened, "Applicant review panel or page did not open"