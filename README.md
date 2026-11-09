# Selenium Automation Tests

Selenium and Pytest coverage for the Alps Jobs application. The suite keeps
the existing candidate, company, job-search, application, pipeline, and review
scenarios while using explicit waits and environment-based credentials.

## Technologies

- Python
- Selenium WebDriver
- Pytest
- pytest-html
- python-dotenv
- Google Chrome and ChromeDriver/Selenium Manager

## Project structure

```text
automation/
├── tests/
│   ├── test_open_site.py
│   ├── test_login.py
│   ├── test_jobs.py
│   ├── test_company_jobs.py
│   ├── test_company_pipeline_review.py
│   └── test_e2e_job_application.py
├── conftest.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

## Prerequisites and installation

1. Install Python 3.11 or newer.
2. Install Google Chrome.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

Selenium Manager normally downloads or locates a compatible ChromeDriver.

## Environment configuration

Copy `.env.example` to `.env` and replace placeholders with the test
accounts supplied for the target environment. Do not commit `.env`.

Required variables:

| Variable | Purpose |
| --- | --- |
| `BASE_URL` | Application base URL |
| `COMPANY_EMAIL` / `COMPANY_PASSWORD` | Company test account |
| `CANDIDATE_EMAIL` / `CANDIDATE_PASSWORD` | Candidate test account |
| `INVALID_PASSWORD` | Deliberately invalid password for the negative login test |

When the four valid account variables are absent, credential-dependent test
files are skipped before WebDriver startup. This allows public checks such as
the home-page test to run without attempting a login. Once valid values are
configured, those tests run normally. `INVALID_PASSWORD` is only used by the
negative-login scenario and should never be a real account password.

## Running tests

Run one test file:

```powershell
pytest tests/test_login.py -v -s
```

Run the complete suite:

```powershell
pytest tests -v -s
```

Generate a self-contained HTML report:

```powershell
pytest tests -v -s --html=reports/report.html --self-contained-html
```

Open `reports/report.html` in a browser after the run. Reports are ignored by
Git.

## Test coverage

- `test_open_site.py`: verifies the home page title and rendered body.
- `test_login.py`: verifies candidate login and the invalid-credentials alert.
- `test_jobs.py`: searches for a job, opens job details, applies, and verifies
  an application confirmation message.
- `test_company_jobs.py`: logs in as a company, creates and publishes a unique
  job, and verifies the created job.
- `test_company_pipeline_review.py`: opens Pipeline, verifies the configured
  job and applicant count, and verifies that review opens in a new route or
  dialog.
- `test_e2e_job_application.py`: creates a unique job, applies as a candidate,
  selects that exact job in Pipeline, verifies the applicant, and opens review.

## Main automated flows

The suite covers authentication, language switching, job creation and
publication, candidate search and application, pipeline job selection, and
applicant review. Pipeline options are located from the visible Angular
Material option role after opening the selector, then matched to the exact
job created during the same E2E run.

## Known limitations

- These are browser integration tests and require the application to be
  reachable and the configured accounts to remain valid.
- Without valid account variables, the login, jobs, company, pipeline, and
  E2E tests are intentionally skipped; no login attempt is made.
- Company pipeline review uses the existing seeded job scenario and therefore
  depends on that job and its applicant data being available.
- Full execution may be blocked by browser-driver, network, application, or
  account availability. Such runs must be reported as blocked or failed rather
  than treated as passing.
