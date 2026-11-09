import os

from dotenv import load_dotenv


load_dotenv()


def optional_setting(name):
    return os.getenv(name, "").strip()


BASE_URL = os.getenv(
    "BASE_URL",
    "https://ui.46-224-109-81.sslip.io",
).rstrip("/")

COMPANY_EMAIL = optional_setting("COMPANY_EMAIL")
COMPANY_PASSWORD = optional_setting("COMPANY_PASSWORD")
CANDIDATE_EMAIL = optional_setting("CANDIDATE_EMAIL")
CANDIDATE_PASSWORD = optional_setting("CANDIDATE_PASSWORD")
INVALID_PASSWORD = optional_setting("INVALID_PASSWORD")

CREDENTIALS_CONFIGURED = all(
    (
        COMPANY_EMAIL,
        COMPANY_PASSWORD,
        CANDIDATE_EMAIL,
        CANDIDATE_PASSWORD,
    )
)
