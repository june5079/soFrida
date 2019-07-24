from flask import Flask, render_template, request, jsonify, g, Response, stream_with_context
from flask_socketio import SocketIO, emit
from threading import Thread
import frida
import json
import os

from getapklist import Getlists
from sflogger import sfLogger
from downloader import Downloader
from assets import Assets
from soFrida import soFrida
from awstester import awsTester

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app, async_mode="threading", engineio_logger=True)
BASE_URI = os.path.dirname(__file__)
getlist = ""

# Use for logging info message
logger = sfLogger("apk_download")

# Use for logging debug message
debuglogger = sfLogger("sofrida")

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
@app.route("/awstest/<package_name>", methods=['GET'])
def awstest_layout(package_name):
  return render_template("awstest.html")
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
def downfile_check(package_name):
  return os.path.exists(os.path.join("./tmp/") + package_name + '.apk')
    
@socketio.on("search", namespace="/apk_download")
def search(data):
  global getlist
  global logger
  print("Getlists(\"%s\", \"%s\")" % (data['mode'].lower().strip(), data['text'].strip()))
  logger.start()
  getlist = Getlists(data['mode'].lower().strip(), data['text'])
  getlist.init_request()
  socketio.start_background_task(target=getlist.get_pkginfo_for_GUI, logger=logger.logger)
  for a in logger.loggenerator():
    data = json.loads(a)
    print(data)
    if data['type'] == "result":
      if downfile_check(data['package_name']):
        data['info']['status'] = "YES"
      else:
        data['info']['status'] = "NO"
      socketio.emit("search_result", data, namespace="/apk_download")
    elif data['type'] == "log":
      socketio.emit("log", data, namespace="/apk_download")
    elif data['type'] == "exit":
      socketio.emit("exit", data, namespace="/apk_download")
      break
  logger.stop()
      
@socketio.on("stop", namespace="/apk_download")
def apk_download_stop(message):
  logger.stop()
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
@socketio.on("download", namespace="/apk_download")
def download(message):
  global downloader
  global getlist
  global logger
  package_list = message['list']
  for package_name in message['list']:
    asset = Assets()
    if not asset.exist(package_name):
      info = getlist.result[package_name]
      asset.add(package_name, info['title'], int(info['popular'].replace(",","")), info['category'])
      asset.close()
  try:
    logger.start()
    socketio.start_background_task(target=downloader.download_packages, package_list=package_list, logger=logger.logger)        
    for a in logger.loggenerator():
      data = json.loads(a)
      if data['step'] == "complete":
        logger.stop()
      socketio.emit("download_step", data, namespace="/apk_download")
  except Exception as e:
    print(e)
    logger.stop()
@socketio.on("select_remove", namespace="/assets")
def select_remove(message):
  print("select_remove")
  asset = Assets()
  for package in message['list']:
    print(package)
    try:
      os.remove(os.path.join("./tmp/") + package + '.apk')
    except:
      pass
    socketio.emit("remove_result", {"result":asset.delete_one(package),"package":package}, namespace="/assets")
@app.route("/analyze/<package_name>", methods=["GET"])
def analyze(package_name):
  global sofrida
  sofrida = soFrida(package_name)
  return render_template("analyze.html", package_name=package_name)

@socketio.on('soFrida_start', namespace="/analyze")
def soFrida_start(message):
  global sofrida
  global debuglogger

  debuglogger.start()
  socketio.start_background_task(target=sofrida.soFrida_start, debuglogger=debuglogger)
  for a in debuglogger.loggenerator():
    data = json.loads(a)
    if data['step'] == "stop":
      if "mode" in data:
        socketio.emit("manual", {}, namespace="/analyze")
      else:
        debuglogger.stop()
        break
    else:
      socketio.emit("analyze_status", data, namespace="/analyze")
  

@socketio.on('soFrida_stop', namespace="/analyze")
def soFrida_stop(message):
  global debuglogger
  global sofrida
  if sofrida != "":
    sofrida.isStop = True
  if "keys" in message:
    print(message)
    asset = Assets()
    asset.update_keys(message['package_name'], message['keys'])
@socketio.on('trace', namespace="/analyze")
def manual_trace(message):
  global sofrida
  global debuglogger
  cls = message['class']
  socketio.start_background_task(target=sofrida.manual_trace, cls=cls, logger=debuglogger)
@socketio.on("awstest_start" ,namespace="/awstest")
def awstest_start(message):
  global logger
  package_name = message['package_name']
  asset = Assets()
  keys = asset.get(package_name)
  logger.start()
  socketio.start_background_task(target=awstest, package_name=package_name, keys=keys)
  for a in logger.loggenerator():
    data = json.loads(a)
    if data['service'] == "stop":
      logger.stop()
      break
    socketio.emit("log", data, namespace="/awstest")
  print("stoped")
def awstest(package_name, keys):
  global logger
  for service in keys['service'].split(","):
    if service == "s3":
      at = awsTester(package_name, keys['access_key_id'], keys['secret_key_id'], keys['session_token'], service, keys['region'], logger.logger)
      at.s3_check(keys['bucket'], "ls")
    elif service == "kinesis":
      at = awsTester(package_name, keys['access_key_id'], keys['secret_key_id'], keys['session_token'], service, keys['region'], logger.logger)
      at.kinesis_check("list_streams")
    elif service == "firehorse":
      at = awsTester(package_name, keys['access_key_id'], keys['secret_key_id'], keys['session_token'], service, keys['region'], logger.logger)
      at.firehose_check("list_delivery_streams")
  logger.logger.info(json.dumps({"service":"stop"}))
if __name__ == '__main__':
    #app.run(host='127.0.0.1', port='8888', debug=True)
    socketio.run(app, host='127.0.0.1', port=8888,  debug=True, log_output=True)