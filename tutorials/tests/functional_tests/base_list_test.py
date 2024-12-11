from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .base_selenium_test import BaseSeleniumTest

class ListSeleniumTest(StaticLiveServerTestCase):
    current_role = None  # Tracks the currently logged-in role for test functions
    roles = ["Admin", "Tutor", "Student"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    def login_as_user(self, username, password):
        self.driver.get(f"{self.live_server_url}/log_in/")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary").click()

    def logout(self):
        self.driver.find_element(By.ID, "user-account-dropdown").click()
        self.driver.find_element(By.XPATH, '//*[@id="navbarSupportedContent"]/ul/li/ul/li[4]/a').click()
        self.driver.get(f"{self.live_server_url}/log_in/")

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
        super().tearDownClass()


class BaseListTests(ListSeleniumTest, BaseSeleniumTest):
    test_accounts = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("Seeding data for all tests in the class...")
        #cls.seed_data()

    def login_with_account(self, account, url):
        self.login_as_user(username=account["username"], password=account["password"])
        self.driver.get(f"{self.live_server_url}{url}")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "table"))
        )
        self.table = self.driver.find_element(By.CLASS_NAME, "table")

    def verify_table_headers(self, expected_headers):
        self.table = self.driver.find_element(By.CLASS_NAME, "table")
        headers=self.table.find_elements(By.TAG_NAME, "th")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "th"))
        )
        headers = [header.text for header in headers]
        self.assertEqual(headers, expected_headers)

    def verify_table_row_count(self, models_len):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
        )
        rows = self.table.find_elements(By.TAG_NAME, "tr")[1:]
        self.assertEqual(len(rows), models_len)

    def verify_row_content(self, row_data_list=None):
        rows = self.table.find_elements(By.TAG_NAME, "tr")[1:]

        if not rows or not row_data_list:
            self.assertEqual(None, row_data_list)
        else:
            for idx, expected_data in enumerate(row_data_list):
                actual_data = [cell.text for cell in rows[idx].find_elements(By.TAG_NAME, "td")]
                self.assertEqual(actual_data, expected_data, f"Row {idx + 1} data does not match expected data.")

    def logout(self):
        super().logout()