import gspread
from flask import Flask, Response, request, jsonify
from main import access_spreadsheet
from main import main as converter 
from concurrent.futures import ThreadPoolExecutor
from db import connect, get_job_id, add_job, job_status

executor = ThreadPoolExecutor(1)

app = Flask(__name__)


@app.route("/status", methods=['POST'])
def status():
    data = request.get_json()
    try:
        job_id = data["jobId"]
    except BaseException:
        return {"message":"Job Id Not Specified"}, 400

    return job_status(job_id), 200


@app.route("/", methods=['POST'])
def convert():
    data = request.get_json()
    try:
        title = data["title"]
    except BaseException:
        return {"message":"Title not specified"}, 400

    main_sheet = data.get("mainSheet", "Sheet1")
    header_rows = data.get("headerRows", 3)
    width_rows = data.get("widthRows", 12)

    try:
        spreadsheet, wksh, _, instruments = access_spreadsheet(title, main_sheet, header_rows)
    except gspread.exceptions.SpreadsheetNotFound:
        return {"message":"Unable to Access Spreadsheet"}, 403
    except gspread.exceptions.WorksheetNotFound:
        return {"message":"Worksheet Not Found"}, 404
    except BaseException:
        return {"message":"Internal Server Error"}, 500

    conn = connect()
    num_instruments = len(instruments)

    running_job_id = get_job_id(conn, title, main_sheet, num_instruments)
    if running_job_id:
        return {"message":"Currently Running", "jobId":running_job_id, "numInstruments":num_instruments}, 200

    new_job_id = add_job(conn, title, main_sheet, num_instruments)
    executor.submit(converter, conn, new_job_id, header_rows,  width_rows)

    return {"message":"Started", "jobId":new_job_id, "numInstruments":num_instruments}, 200

if __name__ == "__main__":
    app.run( debug=True )
