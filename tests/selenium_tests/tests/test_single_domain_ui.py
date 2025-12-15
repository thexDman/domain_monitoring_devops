import pytest
import os
import time
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from tests.selenium_tests.pages.login_page import LoginPage
from tests.selenium_tests.pages.single_domain_modal import SingleDomainModal

pytestmark = pytest.mark.order(9)
THIS_DIR = os.path.dirname(__file__)

@pytest.mark.parametrize(
    "domain",
    [
        "facebook.com",
        "google.com",
        "google.fyi",
        "httpforever.com",
    ]
)
def test_add_single_domain_ui(driver, base_url, domain):
    # -------------------------
    # Login
    # -------------------------
    login_page = LoginPage(driver, base_url)
    login_page.load()
    login_page.login("Selenium_Tester_12345", "St87654321")

    # -------------------------
    # Dashboard
    # -------------------------
    single_modal = SingleDomainModal(driver=driver, base_url=base_url)
    single_modal.load()

    assert single_modal.get_title() == "Dashboard"
    assert single_modal.get_welcome_message()

    # -------------------------
    # Add domain
    # -------------------------
    single_modal.open_add_domain_modal()
    single_modal.add_single_domain(domain=domain)

    # 🔑 wait for async row
    single_modal.wait_for_domain_row(domain)

    # -------------------------
    # Validate domain row
    # -------------------------
    domain_data = single_modal.get_domain_data(domain)
    assert domain_data is not None

    assert isinstance(domain_data["status"], str)
    assert domain_data["status"] != ""

    assert isinstance(domain_data["ssl_issuer"], str)
    assert isinstance(domain_data["ssl_expiration"], str)

    # -------------------------
    # Cleanup
    # -------------------------
    user_domains_path = "./UsersData/Selenium_Tester_12345_domains.json"
    with open(user_domains_path, "w") as f:
        json.dump([], f)
