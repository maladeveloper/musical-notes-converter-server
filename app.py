import gspread
from flask import Flask, Response, request, jsonify
from main import access_spreadsheet
from main import main as converter 
from concurrent.futures import ThreadPoolExecutor
from db import connect, get_job_id, add_job

executor = ThreadPoolExecutor(1)

app = Flask(__name__)


@app.route("/", methods=['POST'])
def convert():
    data = request.get_json()
    try:
        title = data["title"]
    except BaseException:
        return {"message":"Title not specified"}, 400

    main_sheet = data.get("main_sheet", "Sheet1")
    header_rows = data.get("header_rows", 3)
    width_rows = data.get("width_rows", 12)

    try:
        spreadsheet, wksh, instruments =access_spreadsheet(title, main_sheet, header_rows)
    except gspread.exceptions.SpreadsheetNotFound:
        return {"message":"Unable to Access Spreadsheet"}, 403
    except gspread.exceptions.WorksheetNotFound:
        return {"message":"Worksheet Not Found"}, 404
    except BaseException:
        return {"message":"Internal Server Error"}, 500

    conn = connect()
    num_instrument = len(instruments)

    running_job_id = get_job_id(conn, title, main_sheet, num_instrument)
    if running_job_id:
        return {"message":"Currently Running", "job_id":running_job_id}, 200

    new_job_id = add_job(conn, title, main_sheet, num_instrument)
    executor.submit(converter, title, main_sheet, header_rows,  width_rows)

    return {"message":"Started", "job_id":new_job_id}, 200

if __name__ == "__main__":
    app.run( debug=True )
