import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import (
    BASE_URL,
    CANDIDATE_EMAIL,
    CANDIDATE_PASSWORD,
    INVALID_PASSWORD,
    CREDENTIALS_CONFIGURED,
)

pytestmark = pytest.mark.skipif(
    not CREDENTIALS_CONFIGURED,
    reason="Valid test credentials are not configured",
)


def test_valid_login(driver):
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, 15)

    email = wait.until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    password = wait.until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )

 
    email.send_keys(CANDIDATE_EMAIL)
    password.send_keys(CANDIDATE_PASSWORD)
    login_button.click()
    welcome_message = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "app-candidate-dashboard h1.page-title")
        )
    )
    assert welcome_message.text.strip(), "Candidate dashboard heading is empty"


def test_invalid_login(driver):
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, 15)

    email = wait.until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    wrongpassword = wait.until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )

 
    email.send_keys(CANDIDATE_EMAIL)
    wrongpassword.send_keys(INVALID_PASSWORD)
    login_button.click()
    error_message = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='alert']"))
    )
    assert "Invalid credentials" in error_message.text, (
        f"Unexpected invalid-login message: {error_message.text!r}"
    )
