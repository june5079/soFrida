from flask import Flask, render_template, request, jsonify, g, Response, stream_with_context
import frida
import json
import os
from getapklist import Getlists
from threading import Thread
from sflogger import sfLogger
app = Flask(__name__)
BASE_URI = os.path.dirname(__file__)
getlist = ""

logger = sfLogger()

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/apk_download")
def apk_download_layout():
    return render_template("apk_download.html")

@app.route('/stream')
def stream():
  global logger
  if logger != "":
    return Response(logger.loggenerator(), mimetype="text/event-stream")
  else:
    return Response("data: "+json.dumps({"ERROR":{"message":"error"}})+"\n\n", mimetype="text/event-stream")

@app.route("/load_finish")
def load_finish():
  global logger
  logger.stop()
  return jsonify(
    result="success"
  )

@app.route("/search", methods=["POST"])
def search():
  global getlist
  global logger
  print("Getlists(\"%s\", \"%s\")" % (request.json['mode'].lower().strip(), request.json['text'].strip()))
  try:
    logger.start()
    getlist = Getlists(request.json['mode'].lower().strip(), request.json['text'])
    getlist.init_request()
    Thread(target=getlist.get_pkginfo_for_GUI, args=(logger.logger,)).start()
    return jsonify(
      result="success"
    )
  except Exception as e:
    return jsonify(
      result="fail",
      msg=str(e)
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='8888', debug=True)