from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.selenium_tests.pages.dashboard_page import DashboardPage


class SingleDomainModal(DashboardPage):
    """
    Page object for adding a single domain via the dashboard modal.
    Inherits from DashboardPage.
    """

    # -------------------------
    # Locators
    # -------------------------
    add_domain_button = (By.ID, "openAddDomain")
    modal = (By.ID, "addDomainModal")
    form = (By.ID, "addDomainForm")
    domain_input = (By.ID, "domainInput")
    status_box = (By.ID, "addDomainStatus")
    submit_button = (By.CSS_SELECTOR, "#addDomainForm button[type='submit']")

    # -------------------------
    # Modal handling
    # -------------------------
    def wait_for_modal(self):
        return self.wait_for(self.modal)

    def wait_for_modal_to_close(self):
        return self.wait_for_element_to_close(self.modal)

    def open_add_domain_modal(self):
        self.click(self.add_domain_button)
        self.wait_for_modal()

    # -------------------------
    # Form actions
    # -------------------------
    def enter_domain(self, domain: str):
        input_el = self.wait_for(self.domain_input)
        input_el.clear()
        input_el.send_keys(domain)

    def submit(self):
        self.click(self.submit_button)

    def add_single_domain(self, domain: str):
        """
        Add a single domain via the modal.
        Does NOT assume sync backend behavior.
        """
        self.enter_domain(domain)
        self.submit()

    # -------------------------
    # Feedback / async handling
    # -------------------------
    def wait_for_success_indicator(self, timeout=10):
        """
        Wait for *any* feedback to appear in the status box.
        Do NOT rely on exact text (backend/UI may change).
        """
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.status_box)
        )
        return True

    def wait_for_domain_row(self, domain: str, timeout=15):
        """
        Wait until the domain row appears in the dashboard table.
        This handles async scan / render delays.
        """
        def _domain_present(driver):
            return self.get_domain_data(domain) is not None

        WebDriverWait(self.driver, timeout).until(
            lambda d: _domain_present(d)
        )
        return True
