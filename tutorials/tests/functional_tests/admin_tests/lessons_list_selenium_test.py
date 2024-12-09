from tutorials.tests.functional_tests.base_list_test import  ListSeleniumTest, BaseListTests
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AdminTests(BaseListTests):

    def setUp(self):
        # Ensure parent class seeds its data
        super().setUp()
        print("Seeding additional data in StudentTests...")

    @classmethod
    def tearDownClass(cls):
        print("Closing browser and cleaning up after all tests...")
        # Quit the browser if it's initialized
        if cls.driver:
            cls.driver.quit()
            cls.driver = None  # Clean up reference

            #super().tearDownClass()

            # Define multiple student accounts to test
    test_accounts = [
        {"username": "@johndoe", "password": "Qa1", "role": "Admin"},
    ]

    def test_student_lessons(self):
        expected_headers = \
            ["Student", "Teacher", "Subject", "Term Start Date", "Duration", "Frequency", "Notes"]
        row_data_list = [
            ["Charlie Johnson", "Jane Doe", "C++", "Sept. 1, 2024", "2h 30min", "Week", "—"],
            ["Charlie Johnson", "Jane Doe", "Java", "Feb. 1, 2025", "2h 30min", "Month", "—"],
            ["Charlie Johnson", "Jane Doe", "Python", "May 1, 2025", "2h 30min", "Day", "—"],
        ]

        for account in self.test_accounts:
            with self.subTest(account=account):  # Run tests for each account
                self.login_with_account(account, '/dashboard/lessons/')
                self.verify_table_headers(expected_headers)

                table_number = super(BaseListTests, self).lessons_number_for_student()
                self.verify_table_row_count(table_number)
                self.verify_row_content(row_data_list)

                super().logout()  # Logout after each account

    def test_student_lessons_details(self):

        expected_headers = ["Date", "Time", "Status", "Feedback", "Actions"]
        row_data_list = {
            "1":
                [
                    ["Oct. 5, 2024", "noon", "Completed", '', ''],
                    ["Oct. 12, 2024", "noon", "Completed", '', '']
                ],
            "2":
                [
                    ["Oct. 5, 2024", "3:30 p.m.", "Completed", '', ''],
                    ["Oct. 12, 2024", "2 p.m.", "Cancelled", '', '']
                ],
            "3":
                [
                    ["Dec. 6, 2024", "7:30 p.m.", "Completed", '', ''],
                    ["Dec. 12, 2024", "9 a.m.", "Booked", '', '']
                ]
        }

        for account in self.test_accounts:
            with self.subTest(account=account):
                self.login_with_account(account, '/dashboard/lessons/')
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                rows = self.driver.find_elements(By.XPATH, "//tr[@onclick]")
                for index in range(len(rows)):
                    row = rows[index]

                    onclick_attribute = row.get_attribute("onclick")
                    expected_url = onclick_attribute.split("'")[1]
                    full_url = f"{self.live_server_url}{expected_url}"

                    self.driver.get(full_url)
                    WebDriverWait(self.driver, 10).until(
                        EC.url_to_be(full_url)
                    )
                    print(self.driver)
                    self.verify_table_headers(expected_headers)
                    num = expected_url[-2:-1]
                    table_details_number = super(BaseListTests, self).lessons_details_number(num)
                    self.verify_table_row_count(table_details_number)
                    self.verify_row_content(row_data_list[num])
                    self.driver.back()

                super(BaseListTests, self).logout()

    def test_student_can_open_lesson_details(self):

        for account in self.test_accounts:
            with self.subTest(account=account):
                self.login_with_account(account, '/dashboard/lessons/')

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                rows = self.driver.find_elements(By.XPATH, "//tr[@onclick]")
                for row in rows:
                    onclick_attribute = row.get_attribute("onclick")
                    expected_url = onclick_attribute.split("'")[1]

                    row.click()
                    WebDriverWait(self.driver, 10).until(
                        EC.url_to_be(f"{self.live_server_url}{expected_url}")
                    )
                    self.assertEqual(self.driver.current_url, f"{self.live_server_url}{expected_url}")
                    self.driver.back()
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )

                super(BaseListTests, self).logout()