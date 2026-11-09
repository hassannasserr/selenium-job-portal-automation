import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import (
    BASE_URL,
    CANDIDATE_EMAIL,
    CANDIDATE_PASSWORD,
    CREDENTIALS_CONFIGURED,
)

pytestmark = pytest.mark.skipif(
    not CREDENTIALS_CONFIGURED,
    reason="Valid test credentials are not configured",
)


def test_job_search(driver):

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
    email.send_keys(CANDIDATE_EMAIL)
    password.send_keys(CANDIDATE_PASSWORD)

    login_button.click()

    # 4. Verify successful login
    welcome_message = wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "app-candidate-dashboard h1.page-title"
            )
        )
    )


    # 5. Open Jobs from Navbar
    jobs_link = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[href='/jobs']")
        )
    )

    jobs_link.click()

    # 6. Wait for Search input
    search_input = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "q")
        )
    )

    # 7. Search for Frontend jobs
    search_input.send_keys("Frontend")

    find_job_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "form button[type='submit']"
            )
        )
    )

    find_job_button.click()

    # 8. Wait for search results
    job_results = wait.until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "app-job-card-body h3.card-title"
            )
        )
    )

    # Print results
    for job in job_results:
        print("Job:", job.text)

    # 9. Verify search results
    assert any(
        "frontend" in job.text.lower()
        for job in job_results
    )

    # 10. Select first job
    first_job = job_results[0]

    print("Opening job:", first_job.text)

    job_button = first_job.find_element(
        By.XPATH,
        "./ancestor::button[1]"
    )

    job_button.click()

    # 11. Wait until Job Details are selected
    wait.until(
        EC.url_contains("selected=")
    )

    print("Job Details URL:", driver.current_url)

    assert "selected=" in driver.current_url
    job_details_heading = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "main h1, main h2, main h3")
        )
    )
    assert job_details_heading.text.strip(), "Job details heading is empty"

    # 12. Get all Primary buttons after Job Details loads
    primary_buttons = wait.until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "button.btn.btn-primary"
            )
        )
    )

    # 13. Find the visible Apply button
    apply_button = None

    valid_apply_texts = {
        "apply now",
        "jetzt bewerben"
    }

    for button in primary_buttons:

        print(
            "Button:",
            repr(button.text),
            "| Displayed:",
            button.is_displayed(),
            "| Enabled:",
            button.is_enabled()
        )

        if (
            button.is_displayed()
            and button.is_enabled()
            and button.text.strip().lower() in valid_apply_texts
        ):
            apply_button = button
            break

    # 14. Verify Apply button exists
    assert apply_button is not None, "Apply button was not found"

    # 15. Scroll to Apply button
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        apply_button
    )

    # 16. Verify Apply button is visible
    assert apply_button.is_displayed()

    apply_button.click()

    confirmation = wait.until(
        lambda d: next(
            (
                element.text.strip()
                for element in d.find_elements(
                    By.CSS_SELECTOR,
                    "[role='alert'], [role='status']",
                )
                if element.is_displayed()
                and any(
                    phrase in element.text.lower()
                    for phrase in (
                        "application",
                        "applied",
                        "bewerbung",
                        "erfolgreich",
                        "success",
                    )
                )
            ),
            False,
        )
    )
    assert confirmation, "Application confirmation was not displayed"