from flask import Flask, render_template, request, jsonify, g, Response, stream_with_context
import frida
import json
import os
from getapklist import Getlists
app = Flask(__name__)
BASE_URI = os.path.dirname(__file__)
getlist = ""
@app.route("/")
def home():
    return render_template("apk_download.html")
    
@app.route("/apk_download")
def apk_download_layout():
    return render_template("apk_download.html")

def event_stream():
    global getlist
    yield getlist.get_pkginfo()

@app.route('/stream')
def stream():
    global getlist
    if getlist == "":
      return Response("data: "+json.dumps({"EXIT":{"msg":"close"}})+"\n\n", mimetype="text/event-stream")
    else:
      return Response(getlist.get_pkginfo(), mimetype="text/event-stream")

@app.route("/search", methods=["POST"])
def search():
    global getlist
    print("Getlists(\"%s\", \"%s\")" % (request.json['mode'].lower().strip(), request.json['text'].strip()))
    try:
        getlist = Getlists(request.json['mode'].lower().strip(), request.json['text'])
        getlist.init_request()
        return jsonify(
          result="success"
        )
    except Exception as e:
        return jsonify(
            result="fail",
            msg=str(e)
        )

if __name__ == '__main__':
    app.run()