import time
import json
from pprint import pprint
import gspread

HEADER_ROWS = 3
SHEET_1 = "SHEET1"

def colnum_string(num):
    '''Converts coloumn number to google spreadsheet coloumn string'''
    string = ""
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        string = chr(65 + remainder) + string
    return string


def insert_spacing(write_arr, bar_num):
    '''Inserts a space after every bar in the write array'''
    write_rows = 4 # The amount of rows being written for one bar
    spacing = [''] * bar_num
    space_num = write_rows - 1 

    i = space_num
    while i < len(write_arr):
        write_arr.insert(i, spacing)
        i += (space_num + 1)


def get_range(row, chunk_num):
    '''Gets the spreadsheet range for a row and the width'''
    start_range = f"A{row}"
    end_range = f"{colnum_string(chunk_num)}{row}"
    return f"{start_range}:{end_range}"


def rate_limit_wait():
    '''Waits a certain number of seconds to as not to overwhelm rate limit'''
    seconds = 0.75
    time.sleep(seconds)


def produce_write_arr(row_num, chunk_num, new_rows_num):
    '''Produces the write array for a row number which is associated with a instrument'''
    bar_num = 4 # Each bar has 4 values
    ref_count = 2  # First value is instrument name
    write_arr = []

    for row in range(1, new_rows_num + 1):
        row_arr = []
        num_arr = []
        aff_arr = []
        for col in range(1, chunk_num + 1):
            ref_col = colnum_string(ref_count)
            ref_count += 1
            ref = f"{ref_col}{row_num}"
            value = fr'={SHEET_1}!{ref}'
            row_arr.append(value)

            num_ref = f"{ref_col}3"  # Bar number always on row 3
            num_value = fr'={SHEET_1}!{num_ref}'
            num_arr.append(num_value)

            aff_ref = f"{ref_col}{row_num - 1}"
            aff_value = fr'={SHEET_1}!{aff_ref}'
            aff_arr.append(aff_value)

        write_arr.append(num_arr)
        write_arr.append(aff_arr)
        write_arr.append(row_arr)

    insert_spacing(write_arr, bar_num)
    return write_arr


def main(title,chunk_num):
    gc = gspread.service_account(
        filename='./secrets/my-project-1577070881918-23f3103bcd2e.json')
    sh = gc.open(title)
    wksh = sh.sheet1

    cols_with_headers = wksh.col_values(1)
    cols = cols_with_headers[HEADER_ROWS:]  # Remove the header coloumns

    for i in range(len(cols)):
        row_num = i + HEADER_ROWS + 1

        instrument_ref = f"A{row_num}"
        instrument_name = wksh.acell(instrument_ref).value

        if instrument_name:
            try:
                inst_wksh = sh.worksheet(instrument_name)
                sh.del_worksheet(inst_wksh)
            except BaseException:
                pass

            new_rows_num = (
                (len(wksh.row_values(row_num)) - 1) // chunk_num) + 1

            new_sheet_rows_num = 4 * new_rows_num + 1
            inst_wksh = sh.add_worksheet(
                title=instrument_name,
                rows=new_sheet_rows_num,
                cols=chunk_num)

            write_arr = produce_write_arr(row_num, chunk_num, new_rows_num)

            start_range = "A2"
            end_range = f"{colnum_string(len(write_arr[-1]))}{len(write_arr)+1}"
            range_cells = f"{start_range}:{end_range}"
            print(f"Writing data for instrument - {instrument_name}")
            inst_wksh.update(range_cells, write_arr, raw=False)

            num_rows = len(write_arr) + 1

            for row in range(
                    4,
                    num_rows +
                    1,
                    4):  # Format every third row starting at the 3rd row
                rate_limit_wait()

                inst_wksh.format(get_range(row, chunk_num), {
                    "horizontalAlignment": "CENTER",
                })

            for row in range(
                    3,
                    num_rows +
                    1,
                    4):  # Format every third row starting at the 3rd row
                rate_limit_wait()

                inst_wksh.format(get_range(row, chunk_num), {
                    "horizontalAlignment": "CENTER",
                    "textFormat": {
                        "foregroundColor": {
                            "red": (128 / 255),
                            "green": (128 / 255),
                            "blue": (128 / 255)
                        },
                        "fontSize": 12,
                        "italic": True
                    }
                })

            for row in range(
                    2,
                    num_rows +
                    1,
                    4):  # Format every third row starting at the 2nd row
                rate_limit_wait()
                inst_wksh.format(get_range(row, chunk_num), {
                    "backgroundColor": {
                        "red": (224 / 255),
                        "green": (224 / 255),
                        "blue": (224 / 255)
                    },
                    "horizontalAlignment": "LEFT",
                    "textFormat": {
                        "fontSize": 12,
                        "bold": True
                    }
                })

            for row in range(
                    1,
                    num_rows +
                    1,
                    4):  # Merge every third row starting at the 1st row
                rate_limit_wait()

                inst_wksh.merge_cells(get_range(row, chunk_num))

            # Give a title to the page
            title_range = f"A1:{colnum_string(chunk_num)}1"
            inst_wksh.format(title_range, {
                "backgroundColor": {
                    "red": (0 / 255),
                    "green": (76 / 255),
                    "blue": (153 / 255)
                },
                "horizontalAlignment": "CENTER",
                "textFormat": {
                    "foregroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 1.0
                    },
                    "fontSize": 14,
                    "bold": True
                }
            })
            inst_wksh.update('A1', instrument_name)

            # Wait a minute to not exceed rate limit
            time.sleep(10)


if __name__ == "__main__":
    main("Copy of Storm Score", 8)
