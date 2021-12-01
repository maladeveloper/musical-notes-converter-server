import gspread
from flask import Flask, Response, request
from main import main as converter 

app = Flask(__name__)

@app.route("/", methods=['POST'])
def convert():
    data = request.get_json()
    try:
        title = data["title"]
    except KeyError:
        return Response("Title not specified", status=400, mimetype="text/plain")

    width_rows = data.get("width_rows", 12)

    try:
        converter(title, width_rows)
    except gspread.exceptions.SpreadsheetNotFound:
        return Response("Unable to Access Spreadsheet", status=403, mimetype="text/plain")
    except BaseException:
        return Response("Internal Server Error", status=500, mimetype="text/plain")

    return Response("Success", status=200, mimetype="text/plain")

if __name__ == "__main__":
    app.run( debug=True )
