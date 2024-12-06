from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .base_selenium_test import BaseSeleniumTest


class ListSeleniumTest(BaseSeleniumTest):
    current_role = None  # Tracks the currently logged-in role for test functions
    roles = ["Admin", "Tutor", "Student"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def login_as_user(self, username, password):
        self.driver.get(f"{self.live_server_url}/log_in/")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary").click()

    def login(self):
        if not self.current_role:
            raise RuntimeError("`current_role` must be set before running tests.")
        username = self.get_username(self.current_role)
        self.login_as_user(username=username, password="Qa1")
        self.driver.get(f"{self.live_server_url}/dashboard/lessons/")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "table"))
        )
        self.table = self.driver.find_element(By.CLASS_NAME, "table")

    def get_username(self, role):
        role_to_username = {
            "Admin": "@johndoe",
            "Tutor": "@janedoe",
            "Student": "@charlie",
        }
        return role_to_username[role]

    def logout(self):
        self.driver.find_element(By.ID, "user-account-dropdown").click()
        self.driver.find_element(By.XPATH, '//*[@id="navbarSupportedContent"]/ul/li/ul/li[4]/a').click()
