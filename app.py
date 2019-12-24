import os
import requests
import helpers as hlp
import responseRead as rr
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify,Response, session
from werkzeug.utils import secure_filename
import json as js


sAPIkey ="28270d246888957"
jsDir = "../media/testFiles/output/json"

app = Flask(__name__)

# File upload setup > only accept uploads of 4 MB
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024

UPLOAD_FOLDER = "/mnt/3B6FE0A06EB4F24F/mega_sync/06 Persoenliches/06 Projects/00 learningCode/harvardX_CS50/week10_finalProject/projectFolder/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CONTEXT = "test"

with open(os.path.join("../projectFolder/static/storage/category_1.json"),"r") as j:
    jCat1 = js.load(j)




@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST", "GET"])
def upload():

    session["vendor"] = 'none'

    if request.method == "POST" and "file" in request.files:
        if CONTEXT != "test":
            file = request.files["file"]

            session["vendor"] = request.values["vendor"]

            if file.filename == "":
                return jsonify(False)
            
            if not hlp.allowedExtensions(file.filename):
                return jsonify(False)

            # call secure_filename to prevent injection attacks
            sFileName = secure_filename(file.filename)

            # read the file from fileStorage, as Flask's file storage cannot be submitted. Do not save beforehand, otherwise pointer must be reset!
            fileOpen = file.read()

            jResponse = hlp.OCRpost(fileOpen, file.filename, sAPIkey, "ger", hlp.getFileExt(sFileName))

            sNewFileName_js = sFileName.split(".",1)[0].lower() + ".json"
            with open(os.path.join(jsDir,sNewFileName_js), "w") as jsDump:
                js.dump(jResponse,jsDump)

            dReceipt = rr.udf_processJSONtoDB(jResponse["ParsedResults"][0]["ParsedText"])

            # rr.udf_printSectionItems(dReceipt)

        else:
            dReceipt = rr.udf_readJSONdir()

        dResults = list(dReceipt.items())[-1][-1]

        return render_template("results.html", results=dResults, category=jCat1)
    
    return render_template("upload.html")


@app.route("/export", methods=["POST"])
def export():

    csvData_price = request.form.getlist("result_price[]")
    csvData_prod = request.form.getlist("result_product[]")
    csvData_cat = request.form.getlist("result_cat[]")


    csvString = "Vendor;Product;Price;Category;\n"
    

    for i, k in enumerate(csvData_prod):
        
        print(csvData_cat[i])
        if str(csvData_cat[i]) != "-1":
            csvString += session.get("vendor",None)+";"+csvData_prod[i]+";"+csvData_price[i]+";"+csvData_cat[i]+"\n"

    
    

    return Response(csvString, mimetype="text/csv",headers={"Content-disposition":"attachment; filename=myResults_koins.csv"})

@app.route("/final")
def final():

    return render_template("final.html")

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    port = int(os.environ.get("PORT", 8080))     
    app.run(host="0.0.0.0", port=port)