from flask import Flask, render_template, request, jsonify, g, Response, stream_with_context
from flask_socketio import SocketIO, emit
from werkzeug import secure_filename

from threading import Thread
import frida
import json
import os
import time
import argparse
from threading import Event
import gpapi

from getapklist import Getlists
from sflogger import sfLogger
from downloader import Downloader
from assets import Assets
from soFrida import soFrida
from awstester import awsTester
from getinstalledapps import getInstalledApps

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app, async_mode="threading", engineio_logger=True)
BASE_URI = os.path.dirname(__file__)
getlist = ""
proxy = {}

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
@app.route("/keylist")
def keylist_layout():
  asset = Assets()
  key_infos = asset.get_exist_key()
  return render_template("keylist.html", key_infos=key_infos)
@app.route("/installed")
def installed_layout():
  package_list = []
  try:
    inst = getInstalledApps()
    packages = inst.get_Applist()
    for p in packages:
      if downfile_check(p):
        if inst.is_AWSSDK(p):
          package_list.append({"package_name":p, "status": "SDK_EXIST"})
        else:
          package_list.append({"package_name":p, "status": "SDK_NO_EXIST"})
      else:
        package_list.append({"package_name":p, "status": ""})
    return render_template("installed.html", result=package_list)
  except:
    return render_template("installed.html", result=package_list)

@app.route("/awstest/<package_name>", methods=['GET'])
def awstest_layout(package_name):
  asset = Assets()
  ass = asset.get(package_name)
  return render_template("awstest.html", services=ass['service'])
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
  global proxy
  global downloader
  print("Getlists(\"%s\", \"%s\", \"%s\")" % (data['mode'].lower().strip(), data['text'].strip(), data['locale'].split("_")[1]))
  downloader.set_locale(data['locale'])
  logger.start()
  getlist = Getlists(data['mode'].lower().strip(), data['text'], data['locale'].split("_")[1], proxy)
  getlist.init_request()
  socketio.start_background_task(target=getlist.get_pkginfo_for_GUI, logger=logger.logger)
  for a in logger.loggenerator():
    data = json.loads(a)
    if data['type'] == "result":
      if downfile_check(data['package_name']):
        data['info']['status'] = "YES"
      else:
        data['info']['status'] = "NO"
      socketio.emit("search_result", data, namespace="/apk_download")
    elif data['type'] == "log":
      socketio.emit("log", data, namespace="/apk_download")
    elif data['type'] == "exit":
      socketio.emit("exit", data, namespace="/apk_download", callback=logger_stop)
      break
def logger_stop():
  global logger
  print("exitemit")
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
    print("login fail")
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
    info = getlist.result[package_name]
    if not asset.exist(package_name):
      asset.add(package_name, info['title'], int(info['popular'].replace(",","")), info['category'])
      asset.close()
    else:
      ass = asset.get(package_name)
      if ass['popular'] < int(info['popular'].replace(",","")):
        asset.update_asset(package_name, ['title', 'popular', 'category'], [info['title'], int(info['popular'].replace(",","")), info['category'], package_name])
  try:
    logger.start()
    socketio.start_background_task(target=downloader.download_packages, package_list=package_list, logger=logger.logger)        
    for a in logger.loggenerator():
      data = json.loads(a)
      if data['step'] == "complete":
        time.sleep(1)
        logger.stop()
      socketio.emit("download_step", data, namespace="/apk_download")
  except Exception as e:
    print(e)
    logger.stop()
@socketio.on("select_remove", namespace="/assets")
def select_remove(message):
  asset = Assets()
  for package in message['list']:
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

@app.route("/import_file", methods=["POST"])
def import_file():
  global getlist
  global proxy
  global downloader
  
  f = request.files['data']
  f.save(secure_filename(f.filename))
  downloader.set_locale(request.form['locale'])

  file_data = open(f.filename, "r").read().strip()
  pkg_list = file_data.split("\n")
  return jsonify(
    list=pkg_list
  )
@socketio.on("import_file_result", namespace="/apk_download")
def import_file_result(msg):
  global downloader
  global getlist
  get_list = {}
  i = 1
  for pkg_id in msg['pkg_list']:
    getlist = Getlists("pkgid", pkg_id, downloader.locale.split("_")[1], proxy)
    getlist.init_request()
    success = getlist.get_pkginfo_for_socket_io(socketio)
    while getlist.finished == False:
      pass
    get_list[pkg_id] = getlist.result[pkg_id]
    socketio.emit("log", {"type": "log","data":"("+str(i)+"/"+str(len(msg['pkg_list']))+")" +pkg_id+ " pkgid info loaded."}, namespace="/apk_download")
    i+=1
  getlist.result = get_list
  socketio.emit("exit", {"type":"exit"}, namespace="/apk_download", callback=test_func)
def test_func():
  print("exit emit")
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
    asset = Assets()
    asset.update_keys(message['package_name'], message['keys'])
    asset.update_status(message['package_name'], "analyzed")
@socketio.on('trace', namespace="/analyze")
def manual_trace(message):
  global sofrida
  global debuglogger
  cls = message['class']
  socketio.start_background_task(target=sofrida.manual_trace, cls=cls, logger=debuglogger)
at = ""
@socketio.on("awstest_start" ,namespace="/awstest")
def awstest_start(message):
  global logger
  global at
  package_name = message['package_name']
  asset = Assets()
  keys = asset.get(package_name)
  logger.start()
  socketio.start_background_task(target=awstest, package_name=package_name, keys=keys)
  isvuln = False
  for a in logger.loggenerator():
    data = json.loads(a)
    if data['service'] == "stop":
      time.sleep(0.5)
      logger.stop()
      break
    elif data['type'] == "vuln":
      isvuln = isvuln or True
    elif data['type'] == "novuln":
      isvuln = isvuln or False
    socketio.emit("log", data, namespace="/awstest")
  asset.update_one(package_name, "vulnerable", 1 if isvuln else 0)
  at = awsTester(package_name, keys['access_key_id'], keys['secret_key_id'], keys['session_token'], keys['region'])
  socketio.emit("manual_log", {"data":"[!] AWS Configuration Start!!"}, namespace="/awstest")
  at.configure()
  socketio.emit("manual_log", {"data":"[!] AWS Configuration Complete!"}, namespace="/awstest")
@socketio.on("manual_log_cmd", namespace="/awstest")
def manual_log_cmd(data):
  global at
  for line in at.manual_check(data["data"]):
    if line != "":
      socketio.emit("manual_log", {"data":line}, namespace="/awstest")
    
@socketio.on("select_pull", namespace="/installed")
def select_pull(data):
  inst = getInstalledApps()
  for package in data['list']:
    try:
      socketio.emit("pull_result", {"package_name":package,"result":"start"}, namespace="/installed")
      inst.get_app(package)
      socketio.emit("pull_result", {"package_name":package,"result":"SDK_EXIST" if inst.is_AWSSDK(package) else "SDK_NO_EXIST"}, namespace="/installed")
    except Exception as e:
      socketio.emit("pull_result", {"package_name":package,"result":"ERROR", "msg":str(e)}, namespace="/installed")
@app.route("/counties")
def countries():
  return jsonify(
    list=json.loads(open(BASE_URI+"/static/locale.json","r", encoding="utf-8").read())
  )
def awstest(package_name, keys):
  global logger
  at = awsTester(package_name, keys['access_key_id'], keys['secret_key_id'], keys['session_token'], keys['region'], logger.logger)
  auto_check = False
  for service in keys['service'].split(","):
    if service == "s3":
      auto_check = True
      at.s3_check(keys['bucket'], "ls")
    elif service == "kinesis":
      auto_check = True
      at.kinesis_check("list_streams")
    elif service == "firehorse":
      auto_check = True
      at.firehose_check("list_delivery_streams")
  if not auto_check:
    logger.logger.info(json.dumps({"service":"auto_check", "type":"no", "msg":"[!] This app is not using \"s3\", \"kinesis\", \"firehorse\"."}))
  logger.logger.info(json.dumps({"service":"stop"}))
if __name__ == '__main__':
  ap = argparse.ArgumentParser(description='SoFridaGUI')
  ap.add_argument('-p', '--proxy', dest='proxy', required=False, help='http://xxx.xxx.xxx.xxx:YYYY')
  args = ap.parse_args()
  if args.proxy is not None:
    proxy = {"http":args.proxy, "https":args.proxy}
    downloader = Downloader(proxy)
  socketio.run(app, host='127.0.0.1', port=8888,  debug=True, log_output=True)
