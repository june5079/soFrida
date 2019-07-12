from flask import Flask, render_template, request, jsonify, g, Response, stream_with_context
from threading import Thread
import frida
import json
import os

from getapklist import Getlists
from sflogger import sfLogger
from downloader import Downloader
from assets import Assets
from soFrida import soFrida

app = Flask(__name__)
BASE_URI = os.path.dirname(__file__)
getlist = ""

# Use for logging info message
logger = sfLogger()

# Use for logging debug message
debuglogger = sfLogger()

downloader = Downloader()
sofrida = ""

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/apk_download")
def apk_download_layout():
  return render_template("apk_download.html")
@app.route("/assets")
def assets_layout():
  asset = Assets()
  asset_infos = asset.get_all()
  return render_template("assets.html", asset_infos=asset_infos)
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
  global getlist
  package_list = request.json['list']
  for package_name in request.json['list']:
    asset = Assets()
    if not asset.exist(package_name):
      info = getlist.result[package_name]
      asset.add(package_name, info['title'], int(info['popular'].replace(",","")), info['category'])
      asset.close()
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
@app.route("/analyze/<package_name>", methods=["GET"])
def analyze(package_name):
  global sofrida
  sofrida = soFrida(package_name)
  return render_template("analyze.html", package_name=package_name)

@app.route('/soFrida_start')
def soFrida_start():
  global sofrida
  global debuglogger
  debuglogger.start()
  Thread(target=sofrida.soFrida_start, args=(debuglogger,)).start()
  return jsonify(
      result="success"
    )
@app.route('/analyze_status')
def analyze_status():
  global debuglogger
  return Response(debuglogger.loggenerator(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='8888', debug=True)