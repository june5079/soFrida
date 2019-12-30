from gpapi.googleplay import GooglePlayAPI, RequestError, SecurityCheckError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from assets import Assets
from dexparse import DexParse

import requests
import sys, os, time
import traceback
import argparse
import subprocess
import platform
import re
import json

class Downloader:
    def __init__ (self, socketio):
        self.gid = ""
        self.gwd = ""
        self.authSubToken = ""
        self.options = Options()
        self.options.headless = False
        self.chrome_driver = "./chromedriver"
        if platform.system() == "Windows":
            self.chrome_driver = "./chromedriver.exe"
        self.request_url = "https://accounts.google.com/b/0/DisplayUnlockCaptcha"
        self.apkfile_path = os.path.join("./apk/")
        if os.path.exists(self.apkfile_path) == False:
            os.mkdir(self.apkfile_path)
        self.locale = "en_US" #'ko_KR'
        self.timezone = None #'Asia/Seoul'
        self.devices_codenames = GooglePlayAPI.getDevicesCodenames()
        self.devices_codenames.reverse()
        self.proxy = {}
        self.socketio = socketio
        self.namespace = "/apk_download"

    def emit(self, t, data):
        self.socketio.emit(t, data, namespace=self.namespace)

    def set_locale(self, locale):
        self.locale = locale
    def set_proxy(self, proxy):
        self.proxy = proxy

    # LOGIN
    def firstlogin(self, gid, gpw):
        self.server = GooglePlayAPI(self.locale, self.timezone, proxies_config=self.proxy)
        self.gid = gid
        self.gpw = gpw
        for i in range(10):
            try:
                print("try : "+str(i+1)+"/10")
                print('\nLogging in with email and password\n')
                self.server.login(self.gid, self.gpw, None, None)
                self.gsfId = self.server.gsfId
                self.authSubToken = self.server.authSubToken
                return self.secondlogin()
            except SecurityCheckError:
                #traceback.print_exc()
                print("SecurityCheckError")
                return False
            except Exception:
                time.sleep(0.5)
                pass
        print("UNKNOWNERROR")
        return False

    def secondlogin(self):
        print('\nNow trying secondary login with ac2dm token and gsfId saved\n')
        self.server = GooglePlayAPI(self.locale, self.timezone, proxies_config=self.proxy)
        self.server.login(None, None, self.gsfId, self.authSubToken)

        return True

    def download_packages(self, package_list):
        for package in package_list:
            self.startdownload(package)

    def startdownload(self, pkgid):
        self.pkgid = pkgid
        self.asset = Assets()
        self.asset.update_status(self.pkgid, "downloading")
        print('\nAttempting to download %s\n' % self.pkgid)
        self.emit("download_step", {"step":"start", "package":self.pkgid})
        try:
            fl = ""
            for codename in self.devices_codenames:
                self.server = GooglePlayAPI(self.locale, self.timezone, device_codename=codename, proxies_config=self.proxy)
                self.server.login(None, None, self.gsfId, self.authSubToken)
                try:
                    fl = self.server.download(self.pkgid)
                    if fl == "":
                        raise Exception("No Device")
                    with open(self.apkfile_path + self.pkgid + '.apk', 'wb') as apk_file:
                        for chunk in fl.get('file').get('data'):
                            apk_file.write(chunk)
                    print('\n[+] Download successful\n')
                    self.emit("download_step", {"step":"finish", "package":self.pkgid})
                    self.asset.update_status(self.pkgid, "downloaded")
                    self.emit("download_step", {"step":"check","package":self.pkgid})
                    self.check_aws_sdk_common(self.pkgid)
                    break
                except requests.exceptions.SSLError:
                    self.emit("download_step", {"step":"error", "msg":"sslerror", "package":self.pkgid})
                    print("requests.exceptions.SSLError")
                    break
                except Exception:
                    traceback.print_exc()
                    continue
            
        except :
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
            #time.sleep(3)
            pass

        # time.sleep(1)

    def check_aws_sdk(self, pkgid):
        print('[+] Checking AWS_SDK')
        apkfinal_path = self.apkfile_path + pkgid + '.apk'
        s = os.popen('/usr/bin/grep -i "aws-android-sdk" {0}'.format(apkfinal_path)).read()
        if 'matches' in s:
            print ("[!] This Application use AWS_SDK")
            pass
        else:
            print ("[!] NO AWS_SDK FOUND")
            os.remove(apkfinal_path)

    def check_aws_sdk_common(self, pkgid):
        print('[+] Checking AWS_SDK')
        apkfinal_path = self.apkfile_path + pkgid + '.apk'
        dp = DexParse(apkfinal_path)
        cloud_code = dp.cloud_detector()
        if not self.asset.exist(pkgid):
            self.asset.add(pkgid, "", 0, "")
        self.asset.set_cloud(pkgid, cloud_code)
        self.emit("download_step", {"step":"result","package":self.pkgid, "sdk":cloud_code})

    def cloud_detector(self, pkgid):
        print ("Calling cloud detector")
        self.is_ios = False
        apkfinal_path = self.apkfile_path + pkgid + '.apk'
        self.dp = DexParse(apkfinal_path)
        dpcls = self.dp.get_classes()
        class_list = []
        print (type(dpcls))
        for c in dpcls:
            class_list.append(c)
        # Start Detecting
        SDK_Keywords = {"AMZ":'com.amazonaws.auth', "ALB":'com.alibaba.sdk', "AZU":'com.microsoft.azure.storage'}
        try:      
            for code,key in SDK_Keywords.items():
                for c in class_list:
                    if key in c:
                        print ("{0} is exist in pkg".format(key))
                        print (code)
                        break
        except:
            print ("ERROR")