from datetime import datetime
import re
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import (
    BASE_URL,
    CANDIDATE_EMAIL,
    CANDIDATE_PASSWORD,
    COMPANY_EMAIL,
    COMPANY_PASSWORD,
    CREDENTIALS_CONFIGURED,
)

pytestmark = pytest.mark.skipif(
    not CREDENTIALS_CONFIGURED,
    reason="Valid test credentials are not configured",
)

# =========================================================
# Helper Functions
# =========================================================


def login(driver, wait, email, password):
    driver.get(f"{BASE_URL}/login")

    email_input = wait.until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    email_input.clear()
    email_input.send_keys(email)

    password_input = wait.until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    password_input.clear()
    password_input.send_keys(password)

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type='submit']")
        )
    )
    login_button.click()

    wait.until(lambda d: "/login" not in d.current_url)
    print("URL after login:", driver.current_url)



def switch_to_english(driver, wait):
    # Wait until blocking toast/status messages disappear
    wait.until(
        lambda d: all(
            not element.is_displayed()
            for element in d.find_elements(
                By.CSS_SELECTOR,
                "div[role='status'][aria-live='polite']",
            )
        )
    )

    language_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "app-language-menu button[aria-haspopup='menu']",
            )
        )
    )

    # If already English, don't do anything
    if "english" in language_button.text.strip().lower():
        print("Language already English")
        return

    language_button.click()

    language_options = wait.until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "[role='menu'] button[role='menuitem']",
            )
        )
    )

    english_option = None
    for option in language_options:
        if "english" in option.text.strip().lower():
            english_option = option
            break

    assert english_option is not None, "English option not found"
    english_option.click()

    wait.until(
        EC.text_to_be_present_in_element(
            (
                By.CSS_SELECTOR,
                "app-language-menu button[aria-haspopup='menu']",
            ),
            "English",
        )
    )

    print("Language changed to English")



def clear_session(driver):
    driver.execute_script(
        """
        window.localStorage.clear();
        window.sessionStorage.clear();
        """
    )
    driver.delete_all_cookies()
    driver.get(BASE_URL)



def select_pipeline_job(driver, wait, job_title):
    """Select the freshly-created job from the Pipeline job selector.

    The Pipeline UI can already have the wanted job selected. If not, open the
    Angular Material selector and choose the matching visible option.
    """

    # Wait until the new Pipeline selector area is rendered.
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[normalize-space()='Select job']")
        )
    )

    # Prefer the mat-select that belongs to the visible "Select job" field.
    selectors = wait.until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "mat-select"))
    )

    visible_selectors = [
        element
        for element in selectors
        if element.is_displayed() and element.is_enabled()
    ]

    assert visible_selectors, "Visible Pipeline job selector was not found"

    # Use the selector whose current text looks like a job title when possible.
    # If there is only one visible selector, this naturally picks it.
    job_selector = visible_selectors[0]

    selected_text = job_selector.text.strip()
    print("Pipeline selector current value:", repr(selected_text))

    # The newly created job may already be selected automatically.
    if job_title.lower() not in selected_text.lower():
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            job_selector,
        )
        job_selector.click()

        # Angular Material options are rendered in a global overlay. Do not rely
        # on an exact nested span structure because the MDC DOM may change.
        options = wait.until(
            EC.visibility_of_any_elements_located(
                (By.CSS_SELECTOR, "mat-option[role='option'], [role='option']")
            )
        )

        print("Visible Pipeline job options:")
        for option in options:
            print("-", repr(option.text.strip()))

        job_option = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//*[self::mat-option or @role='option']"
                    f"[contains(normalize-space(), '{job_title}')]",
                )
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            job_option,
        )
        job_option.click()

        # Wait until the selector reflects the selected job.
        wait.until(
            lambda d: job_title.lower()
            in job_selector.text.strip().lower()
        )

    # Verify the board itself loaded for that exact job, not just the selector.
    board_job_title = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[self::h1 or self::h2 or self::h3]"
                f"[normalize-space()='{job_title}']",
            )
        )
    )

    print("Pipeline job selected:", board_job_title.text)
    return board_job_title


def get_visible_applicant_count(driver, wait):
    """Find the real numeric applicant counter and ignore helper text containing 'applicants'."""

    def find_counter(d):
        candidates = d.find_elements(
            By.XPATH,
            "//*[contains("
            "translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'applicant'"
            ")]",
        )

        for element in candidates:
            try:
                if not element.is_displayed():
                    continue

                text = element.text.strip()
                if re.fullmatch(r"\d+\s+applicants?", text, flags=re.IGNORECASE):
                    return element
            except Exception:
                # The DOM can re-render while the Pipeline updates.
                continue

        return False

    return wait.until(find_counter)


# =========================================================
# E2E Test
# =========================================================


def test_e2e_job_application(driver):
    wait = WebDriverWait(driver, 15)

    job_title = f"E2E QA Test {datetime.now().strftime('%H%M%S')}"

    print("\n====================================")
    print("E2E TEST STARTED")
    print("Job:", job_title)
    print("====================================")

    # =====================================================
    # STEP 1 - COMPANY LOGIN
    # =====================================================
    print("\nSTEP 1: Company Login")

    login(driver, wait, COMPANY_EMAIL, COMPANY_PASSWORD)
    wait.until(EC.url_contains("/company-dashboard"))

    print("Company login completed:", driver.current_url)
    switch_to_english(driver, wait)

    # =====================================================
    # STEP 2 - OPEN NEW JOB PAGE
    # =====================================================
    print("\nSTEP 2: Open New Job")

    new_job_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "a[href='/company-dashboard/jobs/new']",
            )
        )
    )
    new_job_button.click()

    wait.until(EC.url_contains("/company-dashboard/jobs/new"))
    print("New Job page:", driver.current_url)

    # =====================================================
    # STEP 3 - FILL JOB DETAILS
    # =====================================================
    print("\nSTEP 3: Fill Job Data")

    title_input = wait.until(
        EC.visibility_of_element_located((By.ID, "title"))
    )
    title_input.send_keys(job_title)

    location_input = wait.until(
        EC.visibility_of_element_located((By.ID, "location"))
    )
    location_input.send_keys("Cairo, Egypt")

    description_input = wait.until(
        EC.visibility_of_element_located((By.ID, "description"))
    )
    description_input.send_keys(
        "This job was automatically created for end-to-end QA testing."
    )

    print("Job information entered")

    # =====================================================
    # STEP 4 - SET STATUS TO PUBLISHED
    # =====================================================
    print("\nSTEP 4: Set Job Status = Published")

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
                "//mat-option//span[normalize-space()='Published']",
            )
        )
    )
    published_option.click()

    print("Status selected:", status_dropdown.text)

    # =====================================================
    # STEP 5 - SAVE JOB
    # =====================================================
    print("\nSTEP 5: Save Job")

    save_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Save']")
        )
    )
    save_button.click()

    # =====================================================
    # STEP 6 - CONFIRM SAVE
    # =====================================================
    print("\nSTEP 6: Confirm Save")

    confirm_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[@role='dialog']"
                "//button["
                "normalize-space()='Save' "
                "or normalize-space()='Confirm' "
                "or normalize-space()='Yes' "
                "or normalize-space()='Publish'"
                "]",
            )
        )
    )
    confirm_button.click()

    wait.until(
        lambda d: "/company-dashboard/jobs/new" not in d.current_url
    )

    print("Job created:", job_title)

    # =====================================================
    # STEP 7 - VERIFY COMPANY CREATED THE JOB
    # =====================================================
    print("\nSTEP 7: Verify Created Job")

    created_job = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//*[normalize-space()='{job_title}']")
        )
    )
    assert created_job.is_displayed()

    print("Created job verified")

    # =====================================================
    # STEP 8 - CLEAR COMPANY SESSION
    # =====================================================
    print("\nSTEP 8: Logout Company")
    clear_session(driver)

    # =====================================================
    # STEP 9 - CANDIDATE LOGIN
    # =====================================================
    print("\nSTEP 9: Candidate Login")

    login(driver, wait, CANDIDATE_EMAIL, CANDIDATE_PASSWORD)
    switch_to_english(driver, wait)

    # =====================================================
    # STEP 10 - OPEN JOBS PAGE
    # =====================================================
    print("\nSTEP 10: Open Jobs")

    jobs_link = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[href='/jobs']")
        )
    )
    jobs_link.click()
    wait.until(EC.url_contains("/jobs"))

    # =====================================================
    # STEP 11 - SEARCH FOR CREATED JOB
    # =====================================================
    print("\nSTEP 11: Search Job")

    search_input = wait.until(
        EC.visibility_of_element_located((By.NAME, "q"))
    )
    search_input.clear()
    search_input.send_keys(job_title)

    search_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "form button[type='submit']")
        )
    )
    search_button.click()

    # =====================================================
    # STEP 12 - VERIFY JOB IN SEARCH RESULTS
    # =====================================================
    print("\nSTEP 12: Verify Job")

    job_result = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//app-job-card-body//h3[normalize-space()='{job_title}']",
            )
        )
    )
    assert job_result.is_displayed()

    print("Candidate found:", job_result.text)

    # =====================================================
    # STEP 13 - OPEN JOB
    # =====================================================
    print("\nSTEP 13: Open Job")

    job_button = job_result.find_element(By.XPATH, "./ancestor::button[1]")
    job_button.click()
    wait.until(EC.url_contains("selected="))

    # =====================================================
    # STEP 14 - APPLY
    # =====================================================
    print("\nSTEP 14: Apply")

    primary_buttons = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "button.btn.btn-primary")
        )
    )

    apply_button = None
    valid_apply_texts = {"apply now", "jetzt bewerben"}

    for button in primary_buttons:
        if (
            button.is_displayed()
            and button.is_enabled()
            and button.text.strip().lower() in valid_apply_texts
        ):
            apply_button = button
            break

    assert apply_button is not None, "Apply button was not found"

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        apply_button,
    )
    apply_button.click()

    print("Candidate clicked Apply")

    application_confirmation = wait.until(
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
    assert application_confirmation, "Application confirmation was not displayed"

    # =====================================================
    # STEP 15 - CLEAR CANDIDATE SESSION
    # =====================================================
    print("\nSTEP 15: Logout Candidate")
    clear_session(driver)

    # =====================================================
    # STEP 16 - COMPANY LOGIN AGAIN
    # =====================================================
    print("\nSTEP 16: Company Login Again")

    login(driver, wait, COMPANY_EMAIL, COMPANY_PASSWORD)
    wait.until(EC.url_contains("/company-dashboard"))
    switch_to_english(driver, wait)

    # =====================================================
    # STEP 17 - OPEN PIPELINE
    # =====================================================
    print("\nSTEP 17: Open Pipeline")

    pipeline_link = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[normalize-space()='Pipeline']")
        )
    )
    pipeline_link.click()

    # =====================================================
    # STEP 18 - SELECT AND VERIFY JOB IN PIPELINE
    # =====================================================
    print("\nSTEP 18: Select Job in Pipeline")

    pipeline_job = select_pipeline_job(
        driver,
        wait,
        job_title,
    )
    assert pipeline_job.is_displayed()

    print("Pipeline job found:", pipeline_job.text)

    # =====================================================
    # STEP 19 - VERIFY APPLICANT EXISTS
    # =====================================================
    print("\nSTEP 19: Verify Applicant")

    applicant_count = get_visible_applicant_count(driver, wait)
    applicant_count_text = applicant_count.text.strip()

    print("Applicant count:", applicant_count_text)

    match = re.match(r"(\d+)", applicant_count_text)
    assert match is not None, "Could not parse applicant count"

    count = int(match.group(1))
    assert count >= 1, f"Expected at least 1 applicant, found {count}"

    # Optional stronger verification: try to find the candidate by email fragment.
    candidate_identifier = CANDIDATE_EMAIL.split("@")[0].lower()
    candidate_elements = driver.find_elements(
        By.XPATH,
        "//*[contains("
        "translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
        "'abcdefghijklmnopqrstuvwxyz'), "
        f"'{candidate_identifier}'"
        ")]",
    )

    visible_candidate = None
    for element in candidate_elements:
        try:
            if element.is_displayed():
                visible_candidate = element
                break
        except Exception:
            continue

    if visible_candidate is not None:
        print("Candidate card verified in Pipeline")
    else:
        print(
            "Candidate email text is not fully exposed in the DOM; "
            "applicant count verification passed instead."
        )

    # =====================================================
    # STEP 20 - OPEN APPLICANT REVIEW
    # =====================================================
    print("\nSTEP 20: Review Applicant")

    review_candidates = wait.until(
        lambda d: [
            element
            for element in d.find_elements(
                By.XPATH,
                "//*[self::button or self::a]"
                "[contains("
                "translate(normalize-space(.), "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                "'abcdefghijklmnopqrstuvwxyz'), "
                "'review'"
                ")]",
            )
            if element.is_displayed() and element.is_enabled()
        ]
        or False
    )

    print("Visible Review candidates found:", len(review_candidates))

    assert review_candidates, "Applicant review action was not found"
    review_button = review_candidates[0]
    pipeline_url = driver.current_url
    dialog_count_before = len(
        [
            element
            for element in driver.find_elements(By.CSS_SELECTOR, "[role='dialog']")
            if element.is_displayed()
        ]
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        review_button,
    )
    review_button.click()

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
    print("Review opened successfully")

    # =====================================================
    # FINAL
    # =====================================================
    print("\n====================================")
    print("E2E FLOW PASSED")
    print("Company created job")
    print("Candidate found job")
    print("Candidate applied")
    print("Company selected the job in Pipeline")
    print("Company received applicant")
    print("Company opened Review")
    print("====================================")
