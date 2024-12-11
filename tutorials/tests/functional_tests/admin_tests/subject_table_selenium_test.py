
from tutorials.tests.functional_tests.base_list_test import ListSeleniumTest, BaseListTests
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class StudentTests(BaseListTests):

    @classmethod
    def tearDownClass(cls):
        print("Closing browser and cleaning up after all tests...")
        if cls.driver:
            cls.driver.quit()
            cls.driver = None

    test_accounts = [
        {"username": "@johndoe", "password": "Qa1", "role": "Admin"},
    ]

    '''def test_subject(self):
        expected_headers = \
            ["#", "Name", "Description", "Actions"]
        row_data_list = [
            ["1", "C++", "C++ course", 'Edit Description Delete'],
            ["2", "Java", "Java course", 'Edit Description Delete'],
            ["3", "Python", "Python course", 'Edit Description Delete'],
        ]

        for account in self.test_accounts:
            with self.subTest(account=account):  # Run tests for each account
                self.login_with_account(account, '/dashboard/subjects/')
                self.verify_table_headers(expected_headers)

                table_number = super(BaseListTests, self).lessons_number_for_student()
                self.verify_table_row_count(table_number)
                self.verify_row_content(row_data_list)

                super().logout()  # Logout after each account'''


    def test_student_can_edit_subject_details(self):

        for account in self.test_accounts:
            with self.subTest(account=account):
                self.login_with_account(account, '/dashboard/subjects/')

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                edit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'a.btn.btn-warning.btn-sm')
                for button in edit_buttons:

                    expected_href = button.get_attribute("href")
                    button.click()
                    current_url = self.driver.current_url
                    self.assertEqual(current_url, expected_href)


                    
                    self.driver.back()

                super(BaseListTests, self).logout()