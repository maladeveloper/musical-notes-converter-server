import warnings
import unittest
import sys
import gspread
from db import connect, add_job, delete_job
from main import access_spreadsheet
from main import main as converter


class TestMainConverter(unittest.TestCase):

    def setUp(self):
        self.conn = connect()

        self.title = 'Score1'
        self.main_sheet = 'asd'
        self.header_rows = 3
        self.width_rows = 12

        _, _, _, instruments = access_spreadsheet(
            self.title, self.main_sheet, self.header_rows)

        self.job_id = add_job(
            self.conn,
            self.title,
            self.main_sheet,
            len(instruments))

        if not sys.warnoptions:
            warnings.simplefilter("ignore")

    def test_success(self):
        converter(self.conn, self.job_id, self.header_rows, self.width_rows)

    def test_spreadsheet_access_error(self):
        '''Throws SpreadsheetNotFound error when user does not have access to spreadsheet'''
        title = 'wrongTItleLOLZX'
        try:
            access_spreadsheet(
                title, self.main_sheet, self.header_rows)
        except gspread.exceptions.SpreadsheetNotFound:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_worksheet_not_found_error(self):
        '''Throws a WorksheetNotFound error when main worksheet to run off
        is not found in spreadsheet'''
        main_sheet = 'WrongSheetTitleLOZ'
        try:
            access_spreadsheet(
                self.title, main_sheet, self.header_rows)
        except gspread.exceptions.WorksheetNotFound:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def tearDown(self):
        delete_job(self.conn, self.job_id)


if __name__ == '__main__':
    unittest.main()
