from main import main as converter
import gspread
import unittest
import sys 


class TestMainConverter(unittest.TestCase):

    def setUp(self):
        self.title = 'Score1'
        self.main_sheet = 'asd'
        self.header_rows = 3
        self.width_rows = 12

        if not sys.warnoptions:
            import warnings
            warnings.simplefilter("ignore")
    
    def test_success(self):
        converter(self.title, self.main_sheet, self.header_rows,  self.width_rows)
        
    def test_spreadsheet_access_error(self):
        '''Throws SpreadsheetNotFound error when user does not have access to spreadsheet'''
        title = 'wrongTItleLOLZX'
        try:
            converter(title, self.main_sheet, self.header_rows,  self.width_rows)
        except gspread.exceptions.SpreadsheetNotFound: 
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_worksheet_not_found_error(self):
        '''Throws a WorksheetNotFound error when main worksheet to run off is not found in spreadsheet'''
        main_sheet = 'WrongSheetTitleLOZ'
        try:
            converter(self.title, main_sheet, self.header_rows,  self.width_rows)
        except gspread.exceptions.WorksheetNotFound: 
            self.assertTrue(True)
            return
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
