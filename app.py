import os
import requests
import helpers as hlp
import responseRead as rr
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify,Response, session
from werkzeug.utils import secure_filename
import json as js


sAPIkey ="API KEY"
jsDir = "uploads"

app = Flask(__name__)

# File upload setup > only accept uploads of 4 MB
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CONTEXT = "live"

with open(os.path.join("static/storage/category_1.json"),"r") as j:
    jCat1 = js.load(j)




@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST", "GET"])
def upload():

    session["vendor"] = 'none'

    if request.method == "POST" and "file" in request.files:

        try:
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

                if request.values["lang"]:
                    lang = request.values["lang"]
                else:
                    lang = "ger"

                jResponse = hlp.OCRpost(fileOpen, file.filename, sAPIkey, lang , hlp.getFileExt(sFileName))

                sNewFileName_js = sFileName.split(".",1)[0].lower() + ".json"
                with open(os.path.join(jsDir,sNewFileName_js), "w") as jsDump:
                    js.dump(jResponse,jsDump)

                print(jResponse)
                dReceipt = rr.udf_processJSONtoDB(jResponse["ParsedResults"][0]["ParsedText"])

                os.remove(os.path.join(jsDir,sNewFileName_js))
                # rr.udf_printSectionItems(dReceipt)

            else:
                dReceipt = rr.udf_readJSONdir()

            dResults = list(dReceipt.items())[-1][-1]

            return render_template("results.html", results=dResults, category=jCat1)
        
        except Exception as e: 
            flash(f"Whoops, something went wrong:. Error: {repr(e)}. Please try again or contact the site admin.", "danger")

            return redirect("/")    
    
    return redirect("/")


@app.route("/export", methods=["POST"])
def export():

    try:
        csvData_price = request.form.getlist("result_price[]")
        csvData_prod = request.form.getlist("result_product[]")
        csvData_cat = request.form.getlist("result_cat[]")


        csvString = "Vendor;Product;Price;Category;\n"
        

        for i, k in enumerate(csvData_prod):
            
            # print(csvData_cat[i])
            if str(csvData_cat[i]) != "-1":
                csvString += session.get("vendor",None)+";"+csvData_prod[i]+";"+csvData_price[i]+";"+csvData_cat[i]+"\n"

        
    
        return Response(csvString, mimetype="text/csv",headers={"Content-disposition":"attachment; filename=myResults_koins.csv"})
    
    except Exception as e:
        flash(f"Whoops, something went wrong:. Error: {e}. Please try again or contact the site admin.", "danger")



    return redirect("/")

@app.route("/final")
def final():

    return render_template("final.html")

@app.route("/terms")
def terms():

    return render_template("tcs.html")

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    
    if CONTEXT == 'live':
        port = int(os.environ.get("PORT", 8080))     
        app.run(host="0.0.0.0", port=port)
    else:
        app.run(debug=True)