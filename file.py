
from app import app, Meeting
import csv
import flask_excel as excel

excel.init_excel(app)


@app.route("/file")
def file_op():
    r = []
    with open("sample.txt", "r") as file:
        # file.write("this is a sample file")
        r = file.readlines()
    with open("new_file.txt", "w+") as file1:
        file1.writelines(r)
        file1.seek(0)
        w = file1.readlines()

        print(w)
    return {"new_file": w}


@app.route("/export", methods=['GET'])
def export():
    data = [["meeting_id", "title", "starttime"]]
    res = Meeting.query.all()
    for i in res:
        data.append([i.meeting_id, i.title, i.starttime])
    myFile = open('example2.csv', 'w')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(data)
    return "Writing complete"


@app.route('/download')
def download():
    data = [["meeting_id", "title", "starttime"]]
    res = Meeting.query.all()
    for i in res:
        data.append([i.meeting_id, i.title, i.starttime])
    output = excel.make_response_from_array(data, 'csv')
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
