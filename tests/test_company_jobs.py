 

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pytest

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

def test_company_create_job(driver):
    # 1. Open Login Page
    driver.get(f"{BASE_URL}/login")

    wait = WebDriverWait(driver, 15)

    # 2. Wait for Login fields
    email = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "email")
        )
    )

    password = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "password")
        )
    )

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type='submit']")
        )
    )

    # 3. Login
    email.send_keys(COMPANY_EMAIL)
    password.send_keys(COMPANY_PASSWORD)
    login_button.click()
    # Change language to English
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

    assert english_option is not None

    english_option.click()
    # 4. Navigate to Company Details
    company_details = wait.until(
    EC.visibility_of_element_located(
        (By.LINK_TEXT, "Company details")
    )
)

    new_job_button = wait.until(
    EC.element_to_be_clickable(
        (
            By.CSS_SELECTOR,
            "a[href='/company-dashboard/jobs/new']"
        )
    )
)

    new_job_button.click()
    wait.until(
    EC.url_contains("/company-dashboard/jobs/new")
)

    # Fill Job Title
    job_title = wait.until(
    EC.visibility_of_element_located(
        (By.ID, "title")
    )
)

    job_title_value = (
        f"QA Automation Test Job {datetime.now().strftime('%H%M%S')}"
    )
    job_title.send_keys(job_title_value)


# Fill Location
    location = wait.until(
    EC.visibility_of_element_located(
        (By.ID, "location")
    )
)

    location.send_keys("Cairo, Egypt")


# Fill Description
    description = wait.until(
    EC.visibility_of_element_located(
        (By.ID, "description")
    )
)

    description.send_keys(
    "This job was created automatically using Selenium for QA testing."
    )
    save_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[normalize-space()='Save']")
    )
)
    status_dropdown = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "mat-select[formcontrolname='status']")
    )
)

    status_dropdown.click()
    published_option = wait.until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            "//mat-option//span[normalize-space()='Published']"
        )
    )
)

    published_option.click()   
    print("Title:", job_title.get_attribute("value"))
    print("Location:", location.get_attribute("value"))
    print("Description:", description.get_attribute("value"))

    print("Save displayed:", save_button.is_displayed())
    print("Save enabled:", save_button.is_enabled())
    print("Save disabled attr:", save_button.get_attribute("disabled"))
    save_button.click()
    confirm_button = wait.until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            "//div[@role='dialog']//button[normalize-space()='Save' or normalize-space()='Confirm' or normalize-space()='Yes']"
        )
    )
)

    confirm_button.click()
    wait.until(
    EC.url_contains("/company-dashboard/jobs")
)

    created_job = wait.until(
    EC.visibility_of_element_located(
        (
            By.XPATH,
            f"//*[normalize-space()='{job_title_value}']"
        )
    )
    )

    assert created_job.is_displayed(), "Created job is not visible"