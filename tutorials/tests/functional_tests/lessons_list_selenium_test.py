from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tutorials.forms import LogInForm
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
from time import sleep

from tutorials.tests.functional_tests.base_selenium_test import BaseSeleniumTest


class SeleniumLessonsTest(BaseSeleniumTest):

    @classmethod
    def setUpClass(cls):
        """Set up test environment and perform login once for the entire test class."""
        super().setUpClass()
        cls.admin_login()

    @classmethod
    def admin_login(cls):
        """Log in as an admin."""
        cls.driver.get(f"{cls.live_server_url}/log_in/")
        WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        cls.driver.find_element(By.NAME, "username").send_keys('@johndoe')
        cls.driver.find_element(By.NAME, "password").send_keys('Qa1')
        cls.driver.find_element(By.CSS_SELECTOR, "body > div > div > div > form > input.btn.btn-primary").click()

    def setUp(self):
        """Log in and navigate to the lessons list before each test."""
        self.driver.get(f"{self.live_server_url}/dashboard/lessons/")

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "table"))
        )
        self.table = self.driver.find_element(By.CLASS_NAME, "table")

    def test_lesson_table_headers(self):
        headers = self.table.find_elements(By.TAG_NAME, "th")
        expected_headers = ["Student", "Teacher", "Subject", "Term Start Date", "Duration", "Frequency"]
        actual_headers = [header.text for header in headers]
        self.assertEqual(actual_headers, expected_headers, "Table headers do not match expected headers.")

    def test_lesson_table_length(self):

        self.rows = self.table.find_elements(By.TAG_NAME, "tr")[1:]
        expected_row_count = BaseSeleniumTest.lessons_number(self)
        #print(expected_row_count)
        self.assertEqual(len(self.rows), expected_row_count, f"Expected {expected_row_count} rows, but found {len(self.rows)}.")

    def test_lesson_table_first_row_content(self):
        self.rows = self.table.find_elements(By.TAG_NAME, "tr")[1:]
        first_row = self.rows[0].find_elements(By.TAG_NAME, "td")
        expected_first_row_data = ["@charlie", "@janedoe", "C++", "Sept. 1, 2024", "2h 30min", "Week"]
        actual_first_row_data = [cell.text for cell in first_row]
        self.assertEqual(actual_first_row_data, expected_first_row_data, "First row data does not match expected data.")