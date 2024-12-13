
from tutorials.tests.functional_tests.base_list_test import ListSeleniumTest, BaseListTests
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SubjectTests(BaseListTests):

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
            cls.driver = None

    test_accounts = [
        {"username": "@johndoe", "password": "Qa1", "role": "Admin"},
    ]

    def test_subject(self):
        expected_headers = ["#", "Name", "Description", "Actions"]
        row_data_list = [
            ["1", "C++", "C++ course", 'Edit Description Delete'],
            ["2", "Java", "Java course", 'Edit Description Delete'],
            ["3", "Python", "Python course", 'Edit Description Delete'],
        ]

        for account in self.test_accounts:
            with self.subTest(account=account):
                self.login_with_account(account, '/dashboard/subjects/')
                self.verify_table_headers(expected_headers)

                table_number = super(BaseListTests, self).subjects_number()
                self.verify_table_row_count(table_number)
                self.verify_row_content(row_data_list)

                super().logout()

    def test_admin_can_edit_subject_details(self):
        expected_headers = ["#", "Name", "Description", "Actions"]
        row_data_list = [
            ["1", "C++", "Updated description for testing.", 'Edit Description Delete'],
            ["2", "Java", "Updated description for testing.", 'Edit Description Delete'],
            ["3", "Python", "Updated description for testing.", 'Edit Description Delete'],
        ]

        for account in self.test_accounts:
            with self.subTest(account=account):
                self.login_with_account(account, '/dashboard/subjects/')

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                edit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'a.btn.btn-outline-warning.btn-sm')

                for i in range(len(edit_buttons)):
                    edit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'a.btn.btn-outline-warning.btn-sm')
                    button = edit_buttons[i]
                    expected_href = button.get_attribute("href")
                    button.click()

                    current_url = self.driver.current_url
                    self.assertEqual(current_url, expected_href)

                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "id_description"))
                    )
                    description_input = self.driver.find_element(By.ID, "id_description")
                    description_input.clear()
                    new_description = "Updated description for testing."
                    description_input.send_keys(new_description)

                    update_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                    update_button.click()

                    WebDriverWait(self.driver, 10).until(
                        EC.url_matches('/dashboard/subjects/')
                    )

                table_number = super(BaseListTests, self).subjects_number()
                self.verify_table_row_count(table_number)
                self.verify_row_content(row_data_list)
                super(BaseListTests, self).logout()

    def test_admin_can_delete_subject(self):
        row_data_list = [
            ["1", "C++", "Updated description for testing.", 'Edit Description Delete'],
            ["2", "Java", "Updated description for testing.", 'Edit Description Delete'],
            ["3", "Python", "Updated description for testing.", 'Edit Description Delete'],
        ]

        for account in self.test_accounts:
            with self.subTest(account=account):
                self.login_with_account(account, '/dashboard/subjects/')

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button.btn.btn-outline-danger.btn-sm')[0]

                if not delete_buttons:
                    self.fail("No delete buttons found on the page.")

                delete_buttons.click()

                WebDriverWait(self.driver, 10).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert.accept()

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
                self.assertEqual(len(table_rows), len(row_data_list)-1, "Subject was not deleted.")
                self.logout()

    def test_admin_can_create_subject(self):
        row_data_list = [
            ["1", "C++", "C++ course", 'Edit Description Delete'],
            ["2", "Java", "Java course", 'Edit Description Delete'],
            ["3", "New Subject", "New Subject Description", 'Edit Description Delete'],
            ["4", "Python", "Python course", 'Edit Description Delete'],
        ]

        for account in self.test_accounts:
            with self.subTest(account=account):
                self.login_with_account(account, '/dashboard/subjects/')

                create_subject_button = self.driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary.mb-3')

                if not create_subject_button:
                    self.fail("No 'New Subject' buttons found on the page.")

                create_subject_button.click()

                current_url = self.driver.current_url
                self.assertEqual(current_url, f'{self.live_server_url}/dashboard/subjects/create?')

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "id_name"))
                )

                name_input = self.driver.find_element(By.ID, "id_name")
                name_input.clear()
                new_name = "New Subject"
                name_input.send_keys(new_name)

                description_input = self.driver.find_element(By.ID, "id_description")
                description_input.clear()
                new_description = "New Subject Description"
                description_input.send_keys(new_description)

                submit_buttons = self.driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
                if not submit_buttons:
                    self.fail("No submit buttons found on the page.")
                submit_buttons.click()

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                table_number = super(BaseListTests, self).subjects_number()
                self.verify_table_row_count(table_number)
                self.verify_row_content(row_data_list)

                self.logout()
