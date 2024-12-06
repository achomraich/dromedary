from tutorials.tests.functional_tests.base_list_test import ListSeleniumTest
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class StudentTests(ListSeleniumTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.instance = cls()
        cls.instance.current_role = "Student"
        cls.instance.login()
        cls.table = cls.instance.table

        cls.expected_row_count = cls.instance.lessons_number()

    @classmethod
    def tearDownClass(cls):
        cls.instance.logout()
        super().tearDownClass()

    def test_student_table_headers(self):
        headers = [header.text for header in self.table.find_elements(By.TAG_NAME, "th")]
        expected_headers = ["Student", "Teacher", "Subject", "Term Start Date", "Duration", "Frequency", "Notes", "Action"]
        self.assertEqual(headers, expected_headers)

    def test_student_table_row_count(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
        )

        rows = self.table.find_elements(By.TAG_NAME, "tr")[1:]
        self.assertEqual(len(rows), self.expected_row_count)

    def test_lesson_table_first_row_content(self):
        self.rows = self.table.find_elements(By.TAG_NAME, "tr")[1:]
        first_row = self.rows[0].find_elements(By.TAG_NAME, "td")
        second_row = self.rows[1].find_elements(By.TAG_NAME, "td")
        third_row = self.rows[2].find_elements(By.TAG_NAME, "td")

        expected_first_row_data = ["Charlie Johnson", "Jane Doe", "C++", "Sept. 1, 2024", "2h 30min", "Week", "—", "No Booked Lessons"]
        expected_second_row_data = ["Charlie Johnson", "Jane Doe", "Java", "Feb. 1, 2025", "2h 30min", "Month", "—", "No Booked Lessons"]
        expected_third_row_data = ["Charlie Johnson", "Jane Doe", "Python", "May 1, 2025", "2h 30min", "Day", "—", "Update Lesson"]

        actual_first_row_data = [cell.text for cell in first_row]
        actual_second_row_data = [cell.text for cell in second_row]
        actual_third_row_data = [cell.text for cell in third_row]

        self.assertEqual(actual_first_row_data, expected_first_row_data, "First row data does not match expected data.")
        self.assertEqual(actual_second_row_data, expected_second_row_data, "First row data does not match expected data.")
        self.assertEqual(actual_third_row_data, expected_third_row_data, "First row data does not match expected data.")

