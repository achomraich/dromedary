from tutorials.tests.functional_tests.base_list_test import  ListSeleniumTest, BaseListTests
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class StudenListTests(BaseListTests):

    def setUp(self):
        super().setUp()

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
            cls.driver = None

    test_accounts = [
        {"username": "@johndoe", "password": "Qa1", "role": "Admin"},
    ]

    def test_student_list(self):
        expected_headers = ["#", "Username", "Full Name", "Email", "Actions"]
        row_data_list = [
            ["1", "@charlie", "Charlie Johnson", "charlie.johnson@example.org", "View\nCalendar\nEdit\nDelete"],
            ["2", "@student", "StudentName StudentSurname", "student.example1@example.org", "View\nCalendar\nEdit\nDelete"],
        ]

        for account in self.test_accounts:
            with self.subTest(account=account):
                self.login_with_account(account, '/dashboard/students/')
                self.verify_table_headers(expected_headers)

                table_number = super(BaseListTests, self).student_number()
                self.verify_table_row_count(table_number)
                self.verify_row_content(row_data_list)

                super().logout()
