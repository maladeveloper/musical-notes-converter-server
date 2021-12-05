import sys, os
import warnings
import unittest
import gspread
from src.db import connect, add_job, delete_job
from src.main import access_spreadsheet, converter
from src.main import main

# Disable
def block_print():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enable_print():
    sys.stdout = sys.__stdout__


class TestMainConverter(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore")

        self.conn = connect()

        self.title = 'Score1'
        self.main_sheet = 'asd'
        self.header_rows = 3
        self.width_rows = 12

        _, _, _, instruments = access_spreadsheet(self.title, self.main_sheet, self.header_rows)

        self.job_id = add_job(self.conn, self.title, self.main_sheet, len(instruments))

    def test_success(self):
        block_print()
        main(self.conn, self.job_id, self.header_rows, self.width_rows)
        enable_print()

    def test_rate_limit_hitting_converter_success(self):
        title = 'Score2'
        main_sheet = 'Sheet1'
        # In production seconds is 0.8 seconds but here it is 0 to show rate limiting
        seconds = 0 
        start_row = 0
        _, _, _, instruments = access_spreadsheet(title, main_sheet, self.header_rows)
        job_id = add_job(self.conn, title, main_sheet, len(instruments))

        block_print()
        converter(self.conn, job_id, self.header_rows, self.width_rows, seconds, start_row)
        enable_print()

        #Clean up
        delete_job(self.conn, job_id)

    def test_spreadsheet_access_error(self):
        '''Throws SpreadsheetNotFound error when user does not have access to spreadsheet'''
        title = 'wrongTItleLOLZX'
        try:
            access_spreadsheet(title, self.main_sheet, self.header_rows)
        except gspread.exceptions.SpreadsheetNotFound:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_worksheet_not_found_error(self):
        '''Throws a WorksheetNotFound error when main worksheet to run off
        is not found in spreadsheet'''
        main_sheet = 'WrongSheetTitleLOZ'
        try:
            access_spreadsheet(self.title, main_sheet, self.header_rows)
        except gspread.exceptions.WorksheetNotFound:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def tearDown(self):
        delete_job(self.conn, self.job_id)

