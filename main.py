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
    '''Inserts a space before every bar in the write array'''
    write_rows = 4  # The amount of rows being written for one bar
    spacing = [''] * bar_num

    i = write_rows - 1
    while i <= len(write_arr):
        write_arr.insert(i, spacing)
        i += write_rows

    # Change spaces to be before rather than after
    write_arr.insert(0, write_arr.pop())


def get_range(row, width_rows):
    '''Gets the spreadsheet range for a row and the width'''
    start_range = f"A{row}"
    end_range = f"{colnum_string(width_rows)}{row}"
    return f"{start_range}:{end_range}"


def rate_limit_wait():
    '''Waits a certain number of seconds to as not to overwhelm rate limit'''
    seconds = 0.75
    time.sleep(seconds)


def produce_write_arr(row_num, width_rows, num_data_rows):
    '''Produces the write array for a row number which is associated with a instrument'''
    bar_num = 4  # Each bar has 4 values
    write_arr = []

    ref_count = 2  # First value is instrument name
    for row in range(1, num_data_rows + 1):
        row_arr, num_arr, aff_arr = [], [], []

        for col in range(1, width_rows + 1):
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

        write_arr.extend([num_arr, aff_arr, row_arr])

    insert_spacing(write_arr, bar_num)
    return write_arr


def format_instrument_worksheet(
        inst_wksh,
        new_sheet_rows_num,
        rows_per_data_row,
        width_rows):
    '''Formats the worksheet to make it look pretty.'''
    first_row = 1
    while first_row <= new_sheet_rows_num:
        # Merge every fourth row starting at the 1st row
        rate_limit_wait()
        inst_wksh.merge_cells(get_range(first_row, width_rows))

        # Format every fourth row starting at the 2nd row
        second_row = first_row + 1
        rate_limit_wait()
        inst_wksh.format(get_range(second_row, width_rows), {
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

        # Format every fourth row starting at the 3rd row
        third_row = first_row + 2
        rate_limit_wait()
        inst_wksh.format(get_range(third_row, width_rows), {
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

        # Format every fourth row starting at the 4th  row
        fourth_row = first_row + 3
        rate_limit_wait()
        inst_wksh.format(get_range(fourth_row, width_rows), {
            "horizontalAlignment": "CENTER",
        })

        first_row += rows_per_data_row


def add_worksheet_title(inst_wksh, instrument_name, width_rows):
    '''Adds a title to the worksheet'''
    title_range = f"A1:{colnum_string(width_rows)}1"
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


def delete_old_sheet(spreadsheet, instrument_name):
    '''Deletes the old sheet for the instrument if it exists'''
    try:
        inst_wksh = spreadsheet.worksheet(instrument_name)
        spreadsheet.del_worksheet(inst_wksh)
    except BaseException:
        pass

def add_worksheet_data(inst_wksh, write_arr):
    '''Adds the notes data to the instrument worksheet'''
    start_range = "A1"
    end_range = f"{colnum_string(len(write_arr[-1]))}{len(write_arr)+1}"
    range_cells = f"{start_range}:{end_range}"
    inst_wksh.update(range_cells, write_arr, raw=False)

def access_spreadsheet(title):
    gspreadsheet = gspread.service_account(
        filename='./secrets/my-project-1577070881918-23f3103bcd2e.json')
    return gspreadsheet.open(title)

def main(title, width_rows):
    rows_per_data_row = 4

    spreadsheet = access_spreadsheet(title)
    wksh = spreadsheet.sheet1

    cols_with_headers = wksh.col_values(1)
    cols = cols_with_headers[HEADER_ROWS:]  # Remove the header coloumns

    for i in range(len(cols)):
        row_num = i + HEADER_ROWS + 1
        instrument_name = wksh.acell(f"A{row_num}").value

        if not instrument_name: continue

        delete_old_sheet(spreadsheet, instrument_name)

        num_data_rows = (
            (len(wksh.row_values(row_num)) - 1) // width_rows) + 1

        new_sheet_rows_num = num_data_rows * rows_per_data_row

        inst_wksh = spreadsheet.add_worksheet(
            title=instrument_name,
            rows=new_sheet_rows_num,
            cols=width_rows)

        print(f"Writing data for instrument - {instrument_name}")
        write_arr = produce_write_arr(row_num, width_rows, num_data_rows)
        add_worksheet_data(inst_wksh, write_arr)

        format_instrument_worksheet(
            inst_wksh,
            new_sheet_rows_num,
            rows_per_data_row,
            width_rows)

        add_worksheet_title(inst_wksh, instrument_name, width_rows)

        # Wait 10sec to not exceed rate limit
        time.sleep(10)


if __name__ == "__main__":
    main("Copy of Storm Score", 8)
