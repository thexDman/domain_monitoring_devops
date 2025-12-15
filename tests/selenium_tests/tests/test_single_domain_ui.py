import pytest
import uuid

from tests.selenium_tests.pages.login_page import LoginPage
from tests.selenium_tests.pages.single_domain_modal import SingleDomainModal

pytestmark = pytest.mark.order(9)

def test_add_single_domain_ui(driver, base_url):
    domain = f"ui-{uuid.uuid4().hex[:8]}.example.com"

    login_page = LoginPage(driver, base_url)
    login_page.load()
    login_page.login("Selenium_Tester_12345", "St87654321")

    modal = SingleDomainModal(driver=driver, base_url=base_url)
    modal.load()

    assert modal.get_title() == "Dashboard"

    modal.open_add_domain_modal()
    modal.add_single_domain(domain)

    modal.wait_for_domain_row(domain)

    domain_data = modal.get_domain_data(domain)
    assert domain_data is not None
    assert domain_data["status"]
