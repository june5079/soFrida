from flask import Flask, render_template, request, jsonify, g, Response, stream_with_context
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from threading import Thread
import frida
import json
import os
import time
import argparse
from threading import Event
import gpapi

from getapklist import Getlists
from downloader import Downloader
from assets import Assets
from soFrida import soFrida
from awstester import awsTester

from FridaGUI import FridaGUI

app = Flask(__name__)
fg = FridaGUI()
app.secret_key = "secret"
socketio = SocketIO(app, async_mode="threading", engineio_logger=True)
BASE_URI = os.path.dirname(__file__)

getlist = Getlists(socketio)
downloader = Downloader(socketio)
sofrida = soFrida(socketio)
at = awsTester(socketio)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/apk_download")
def apk_download_layout():
  return render_template("apk_download.html")
@app.route("/assets")
def assets_layout():
  asset = Assets()
  asset_infos = asset.get_exist_sdk()
  return render_template("assets.html", asset_infos=asset_infos)
@app.route("/keylist")
def keylist_layout():
  asset = Assets()
  key_infos = asset.get_exist_key()
  return render_template("keylist.html", key_infos=key_infos)

#device
@app.route("/devices", methods=["GET"])
def devices():
  devices = fg.get_device_list()
  return render_template("modal/device.html", devices=devices)
@app.route("/device", methods=["GET"])
def device():
  return jsonify(serial=fg.serial)
@socketio.on("connect", namespace="/device")
def installed_connect():
  if fg.serial != "":
    print(fg.serial)
    device = fg.get_current_device()
    socketio.emit("device", {"devices":[device]}, namespace="/device")
  else:
    print("no serial")
    devices = fg.get_device_list()
    print(devices)
    socketio.emit("device", {"devices":devices}, namespace="/device") 

#installed
@app.route("/installed")
def installed_layout():
  return render_template("installed.html")
@app.route("/installed_list/<serial>", methods=["GET"])
def installed_list_layout(serial):
  package_list = fg.installed_list(serial)
  return render_template("card/installed.html", result=package_list)
@socketio.on("pull", namespace="/installed")
def apk_pull(data):
  for package in data['list']:
    fg.apk_pull(package)
    socketio.emit("pull_res", {"name":package['name']}, namespace="/installed")

#download
@app.route("/downloaded")
def downloaded_layout():
  downloaded_list = fg.get_downloaded_list()
  return render_template("downloaded.html", result=downloaded_list)
@socketio.on("remove", namespace="/donwloaded")
def apk_remove(data):
  for package in data['list']:
    fg.apk_remove(package)
    socketio.emit("remove_res", {"name":package}, namespace="/donwloaded")

#dex
@app.route("/dex/<package_name>")
def dex(package_name):
  fg.package_name = package_name
  return render_template("dex.html")
@app.route("/classes")
def get_classes():
  return get_classes_apk(fg.package_name)
@app.route("/classes/<package_name>", methods=["GET"])
def get_classes_apk(package_name):
  classes = fg.get_dex(package_name)
  class_list = []
  for c in classes:
    class_list.append(c)
  return jsonify(
    result=class_list
  )
@app.route("/class_table", methods=["POST"])
def class_table():
  class_list = request.get_json(force=True)['list']
  return render_template("card/class_table.html", result=class_list)

@app.route("/methods/<class_name>", methods=["GET"])
def methods(class_name):
  methods = fg.get_methods(class_name)
  return render_template("card/method_table.html", result=methods)
@app.route("/code/<class_name>/<index>", methods=["GET"])
def code(class_name, index):
  code = fg.intercept_code(class_name, index)
  return render_template("card/code.html", code=code)
@app.route("/codes/<class_name>", methods=["POST"])
def codes(class_name):
  print(class_name)
  index_list = request.get_json(force=True)['list']
  print(index_list)
  code = ""
  for index in index_list:
    code += fg.intercept_code(class_name, index)+"\n"
  return render_template("card/code.html", code=code)

@app.route("/load", methods=["POST"])
def load():
  fg.loaded = False
  data = request.get_json(force=True)
  code = data['code']
  pid = int(data['pid'])
  package_name = data['package_name']
  print(code)
  print(pid)
  print(package_name)
  def callback(message, data):
    print(message)
    if "payload" in message:
      socketio.emit("load_result", message['payload'], namespace="/load")
    else:
      socketio.emit("load_error", message['stack'], namespace="/load")
  socketio.start_background_task(fg.load, pid=pid, js=code, callback=callback)
  #fg.load(pid, code, callback)
  return jsonify(
    result = "success"
  )
@app.route("/spawn", methods=["POST"])
def spawn():
  fg.loaded = False
  data = request.get_json(force=True)
  code = data['code']
  package_name = data['package_name']
  process = fg.spawn()
  print(process['pid'])
  print(code)
  print(package_name)
  socketio.emit("process", {"processes":[process]}, namespace="/process")
  def callback(message, data):
    print(message)
    if "payload" in message:
      socketio.emit("load_result", message['payload'], namespace="/load")
    else:
      socketio.emit("load_error", message['stack'], namespace="/load")
  socketio.start_background_task(fg.load_and_resume, pid=process['pid'], js=code, callback=callback)
  return jsonify(
    result = "success"
  )
@socketio.on("script_unload", namespace="/load")
def unload():
  fg.loaded = False
@app.route("/reload", methods=["POST"])
def reload():
  fg.loaded = False
  data = request.get_json(force=True)
  code = data['code']
  pid = int(data['pid'])
  package_name = data['package_name']
  print(code)
  print(pid)
  print(package_name)
  return jsonify(
      result = "success"
  )
@socketio.on("connect", namespace="/process")
def connect_process():
  process_list = fg.get_process()
  if process_list == None:
    socketio.emit("process", {"processes":[]}, namespace="/process")
  else:
    if len(process_list) == 0:
      process = fg.spawn()
      fg.resume(process['pid'])
      socketio.emit("process", {"processes":[process]}, namespace="/process")
    else:
      socketio.emit("process", {"processes":process_list}, namespace="/process")



#aws
@app.route("/awstest/<package_name>", methods=['GET'])
def awstest_layout(package_name):
  asset = Assets()
  ass = asset.get(package_name)
  return render_template("awstest.html", services=ass['service'])

def downfile_check(package_name):
  return os.path.exists(os.path.join("./apk/") + package_name + '.apk')
    
@socketio.on("search", namespace="/apk_download")
def search(data):
  print("Getlists(\"%s\", \"%s\", \"%s\")" % (data['mode'].lower().strip(), data['text'].strip(), data['locale'].split("_")[1]))
  downloader.set_locale(data['locale'])
  
  getlist.init_request(data['mode'].lower().strip(), data['text'], data['locale'].split("_")[1])
  socketio.start_background_task(target=getlist.get_pkginfo)

@app.route("/google_login_check", methods=['GET'])
def google_login_check():
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
    socketio.start_background_task(target=downloader.download_packages, package_list=package_list)        

@socketio.on("select_remove", namespace="/assets")
def select_remove(message):
  asset = Assets()
  for package in message['list']:
    try:
      os.remove(os.path.join("./apk/") + package + '.apk')
    except:
      pass
    socketio.emit("remove_result", {"result":asset.delete_one(package),"package":package}, namespace="/assets")
@app.route("/analyze/<package_name>", methods=["GET"])
def analyze(package_name):
  sofrida.set_pkgid(package_name)
  return render_template("analyze.html", package_name=package_name)

@app.route("/import_file", methods=["POST"])
def import_file():
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
  get_list = {}
  i = 1
  for pkg_id in msg['pkg_list']:
    getlist.init_request("pkgid", pkg_id, downloader.locale.split("_")[1])
    getlist.get_pkginfo_for_socket_io()
    while getlist.finished == False:
      pass
    get_list[pkg_id] = getlist.result[pkg_id]
    socketio.emit("log", {"type": "log","data":"("+str(i)+"/"+str(len(msg['pkg_list']))+")" +pkg_id+ " pkgid info loaded."}, namespace="/apk_download")
    i+=1
  getlist.result = get_list
  socketio.emit("exit", {}, namespace="/apk_download", callback=test_func)
def test_func():
  print("exit emit")

@socketio.on('soFrida_start', namespace="/analyze")
def soFrida_start(message):
  socketio.start_background_task(target=sofrida.soFrida_start)
  
@socketio.on('soFrida_stop', namespace="/analyze")
def soFrida_stop(message):
  sofrida.isStop = True
  if "keys" in message:
    asset = Assets()
    asset.update_keys(message['package_name'], message['keys'])
    asset.update_status(message['package_name'], "analyzed")

@socketio.on("awstest_start" ,namespace="/awstest")
def awstest_start(message):
  package_name = message['package_name']
  asset = Assets()
  keys = asset.get(package_name)
  socketio.start_background_task(target=awstest, package_name=package_name, keys=keys)
  
@socketio.on("manual_log_cmd", namespace="/awstest")
def manual_log_cmd(data):
  global at
  for line in at.manual_check(data["data"]):
    if line != "":
      socketio.emit("manual_log", {"data":line}, namespace="/awstest")
    
@app.route("/counties")
def countries():
  return jsonify(
    list=json.loads(open(BASE_URI+"/static/locale.json","r", encoding="utf-8").read())
  )
def awstest(package_name, keys):
  at.set_keys(package_name, keys['access_key_id'], keys['secret_key_id'], keys['session_token'], keys['region'])
  auto_check = False
  isvuln = False
  for service in keys['service'].split(","):
    if service == "s3":
      auto_check = True
      isvuln = isvuln or at.s3_check(keys['bucket'], "ls")
    elif service == "kinesis":
      auto_check = True
      isvuln = isvuln or at.kinesis_check("list_streams")
    elif service == "firehose":
      auto_check = True
      isvuln = isvuln or at.firehose_check("list_delivery_streams")
  asset = Assets()
  asset.update_one(package_name, "vulnerable", 1 if isvuln else 0)
  if not auto_check:
    socketio.emit("log", {"service":"auto_check", "type":"no", "msg":"[!] This app is not using \"s3\", \"kinesis\", \"firehose\"."}, namespace="/awstest")

  socketio.emit("manual_log", {"data":"[!] AWS Configuration Start!!"}, namespace="/awstest")
  at.configure()
  socketio.emit("manual_log", {"data":"[!] AWS Configuration Complete!"}, namespace="/awstest")

#ios_process
@app.route("/ios_process")
def ios_process_layout():
    return render_template("ios_process.html")
@app.route("/ios_process_list/<serial>", methods=["GET"])
def ios_process_list_layout(serial):
  process_list = fg.get_ios_process_list(serial)
  return render_template("card/ios_process.html", result=process_list)



if __name__ == '__main__':
  ap = argparse.ArgumentParser(description='SoFridaGUI')
  ap.add_argument('-p', '--proxy', dest='proxy', required=False, help='http://xxx.xxx.xxx.xxx:YYYY')
  args = ap.parse_args()

  if args.proxy is not None:
    proxy = {"http":args.proxy, "https":args.proxy}
    downloader.set_proxy(proxy)
    getlist.set_proxy(proxy)

  socketio.run(app, host='127.0.0.1', port=8888,  debug=True, log_output=True)
