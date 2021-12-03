import gspread
from flask import Flask, Response, request
from main import access_spreadsheet
from main import main as converter 

app = Flask(__name__)

@app.route("/", methods=['POST'])
def convert():
    data = request.get_json()
    try:
        title = data["title"]
    except BaseException:
        return Response("Title not specified", status=400, mimetype="text/plain")

    main_sheet = data.get("main_sheet", "Sheet1")
    header_rows = data.get("header_rows", 3)
    width_rows = data.get("width_rows", 12)

    try:
        access_spreadsheet(title, main_sheet, header_rows)
    except gspread.exceptions.SpreadsheetNotFound:
        return Response("Unable to Access Spreadsheet", status=403, mimetype="text/plain")
    except gspread.exceptions.WorksheetNotFound:
        return Response("Worksheet Not Found", status=404, mimetype="text/plain")
    except BaseException:
        return Response("Internal Server Error", status=500, mimetype="text/plain")

    return Response("Started", status=200, mimetype="text/plain")

if __name__ == "__main__":
    app.run( debug=True )
