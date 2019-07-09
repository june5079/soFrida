from flask import Flask, render_template, request, jsonify, g, Response, stream_with_context
from threading import Thread
import frida
import json
import os

from getapklist import Getlists
from sflogger import sfLogger
from downloader import Downloader
app = Flask(__name__)
BASE_URI = os.path.dirname(__file__)
getlist = ""


logger = sfLogger()

# Use for logging debug message
debuglogger = sfLogger()

downloader = Downloader()

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

@app.route("/google_login_check", methods=['GET'])
def google_login_check():
  global downloader
  if downloader.authSubToken == "":
    return jsonify(
      result="fail"
    )
  else:
    return jsonify(
      result="success"
    )
@app.route("/google_login", methods=['POST'])
def google_login():
  global downloader
  id = request.form['id']
  pw = request.form['pw']
  if downloader.firstlogin(id, pw):
    return jsonify(
      result="success"
    )
  else:
    return jsonify(
      result="fail"
    )
@app.route("/download", methods=['POST'])
def download():
  global downloader
  package_list = request.json['list']
  try:
    Thread(target=downloader.download_packages, args=(package_list,)).start()
    return jsonify(
      result="success"
    )
  except Exception as e:
    print(e)
    return jsonify(
      result="fail"
    )
if __name__ == '__main__':
    app.run(host='127.0.0.1', port='8888', debug=True)