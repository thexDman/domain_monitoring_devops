from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.selenium_tests.pages.dashboard_page import DashboardPage


class BulkUploadModal(DashboardPage):
    bulk_upload_button = (By.ID, "openBulkUpload")
    file_input = (By.CSS_SELECTOR, "#bulkUploadForm input[type='file']")
    upload_button = (By.CSS_SELECTOR, "#bulkUploadForm button[type='submit']")
    upload_status = (By.ID, "bulkUploadStatus")
    bulk_modal = (By.ID, "bulkUploadModal")

    def open_bulk_upload(self):
        self.click(self.bulk_upload_button)
        self.wait_for(self.bulk_modal)

    def upload_bulk(self, file_path):
        self.upload_file_enter_path(self.file_input, file_path)
        self.click(self.upload_button)

    def _final_message(self):
        element = self.wait.until(
            EC.presence_of_element_located(self.upload_status)
        )

        message = element.text.strip()
        css = element.get_attribute("class")

        # Ignore transient states
        if not message:
            return False
        if "loading" in css.lower():
            return False
        if message.lower().startswith("uploading"):
            return False

        return message

    def get_final_status(self):
        return WebDriverWait(self.driver, 15).until(
            lambda d: self._final_message(),
            "Bulk upload final status did not appear"
        )
