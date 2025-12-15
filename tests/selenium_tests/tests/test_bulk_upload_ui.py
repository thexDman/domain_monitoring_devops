import os
import pytest

from tests.selenium_tests.pages.login_page import LoginPage
from tests.selenium_tests.pages.bulk_upload_modal import BulkUploadModal
from tests.selenium_tests.utils.domain_factory import (
    generate_fixed_domain_file,
    remove_fixed_file_path,
)

from tests.api_tests.Aux_Library import (
    check_login_user,
    remove_domains,
)

pytestmark = pytest.mark.order(10)

TEST_USERNAME = "Selenium_Tester_12345"
TEST_PASSWORD = "St87654321"

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(TEST_DIR, "selenium_temp")
os.makedirs(TEMP_DIR, exist_ok=True)


@pytest.fixture
def cleanup_domains():
    """
    Collect domains added during test
    and remove them via API.
    """
    domains = []

    def _register(domain):
        domains.append(domain)

    yield _register

    if not domains:
        return

    login = check_login_user(TEST_USERNAME, TEST_PASSWORD)
    token = login.json().get("token")

    if token:
        remove_domains(token=token, domains=domains)


def test_bulk_upload_ui(driver, base_url, cleanup_domains):
    # -------------------------------------------------
    # Login (UI)
    # -------------------------------------------------
    login_page = LoginPage(driver, base_url)
    login_page.load()
    login_page.login(TEST_USERNAME, TEST_PASSWORD)

    # -------------------------------------------------
    # Dashboard (NO load here!)
    # -------------------------------------------------
    bulk_modal = BulkUploadModal(driver=driver, base_url=base_url)

    # Wait until dashboard is really loaded
    bulk_modal.wait_for_active_dashboard()

    assert bulk_modal.get_title() == "Dashboard"
    assert bulk_modal.get_welcome_message()

    # -------------------------------------------------
    # Open bulk upload modal
    # -------------------------------------------------
    bulk_modal.open_bulk_upload()

    # -------------------------------------------------
    # Generate domain file
    # -------------------------------------------------
    domains_file_path, check_domains_json_path, domains = \
        generate_fixed_domain_file(TEMP_DIR)

    for domain in domains:
        cleanup_domains(domain)

    # -------------------------------------------------
    # Upload file
    # -------------------------------------------------
    bulk_modal.upload_bulk(file_path=domains_file_path)

    final_status = bulk_modal.get_final_status()
    assert "completed" in final_status.lower()

    # -------------------------------------------------
    # Wait for dashboard refresh
    # -------------------------------------------------
    bulk_modal.wait_for_active_dashboard()

    # -------------------------------------------------
    # Validate domain rows (structure only)
    # -------------------------------------------------
    for domain in domains:
        row = bulk_modal.get_domain_data(domain)
        assert row is not None

        assert isinstance(row["status"], str)
        assert row["status"] != ""

        assert isinstance(row["ssl_issuer"], str)
        assert isinstance(row["ssl_expiration"], str)

    # -------------------------------------------------
    # Cleanup temp files
    # -------------------------------------------------
    remove_fixed_file_path(
        check_file=check_domains_json_path,
        domains_file=domains_file_path
    )
