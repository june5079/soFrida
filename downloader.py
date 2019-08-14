from gpapi.googleplay import GooglePlayAPI, RequestError, SecurityCheckError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from assets import Assets

import sys, os, time
import traceback
import argparse
import subprocess
import platform
import re
import json

class Downloader:
    def __init__ (self):
        self.gid = ""
        self.gwd = ""
        self.authSubToken = ""
        self.options = Options()
        self.options.headless = False
        self.chrome_driver = "./chromedriver"
        if platform.system() == "Windows":
            self.chrome_driver = "./chromedriver.exe"
        self.request_url = "https://accounts.google.com/b/0/DisplayUnlockCaptcha"
        self.proxy = {}
        self.apkfile_path = os.path.join("./tmp/")
        if os.path.exists(self.apkfile_path) == False:
            os.mkdir(self.apkfile_path)
        self.server = GooglePlayAPI('ko_KR', 'Asia/Seoul', proxies_config=self.proxy)
        self.devices_codenames = GooglePlayAPI.getDevicesCodenames()
        self.devices_codenames.reverse()

    # LOGIN
    def firstlogin(self, gid, gpw):
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
        self.server = GooglePlayAPI('ko_KR', 'Asia/Seoul', proxies_config=self.proxy)
        self.server.login(None, None, self.gsfId, self.authSubToken)

        # call DOWNLOAD
        self.startdownload()
        return True

    def download_packages(self, package_list, logger=""):
        for package in package_list:
            self.startdownload(package, logger)
        logger.info(json.dumps({"step":"complete"}))

    def startdownload(self, pkgid="", logger=""):
        self.pkgid = pkgid
        if self.pkgid == "":
            return
        self.asset = Assets()
        self.asset.update_status(self.pkgid, "downloading")
        print('\nAttempting to download %s\n' % self.pkgid)
        logger.info(json.dumps({"step":"start","package":self.pkgid}))
        try:
            fl = ""
            for codename in self.devices_codenames:
                self.server = GooglePlayAPI('ko_KR', 'Asia/Seoul', device_codename=codename, proxies_config=self.proxy)
                self.server.login(None, None, self.gsfId, self.authSubToken)
                try:
                    fl = self.server.download(self.pkgid)
                    break
                except Exception as e:
                    continue
            if fl == "":
                raise Exception("No Device")
            with open(self.apkfile_path + self.pkgid + '.apk', 'wb') as apk_file:
                for chunk in fl.get('file').get('data'):
                    apk_file.write(chunk)
            print('\n[+] Download successful\n')
            logger.info(json.dumps({"step":"finish","package":self.pkgid}))
            self.asset.update_status(self.pkgid, "downloaded")
            logger.info(json.dumps({"step":"check","package":self.pkgid}))
            self.check_aws_sdk_common(self.pkgid, logger)
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

    def check_aws_sdk_common(self, pkgid, logger=""):
        print('[+] Checking AWS_SDK')
        apkfinal_path = self.apkfile_path + pkgid + '.apk'
        
        if re.search(b'(?i)aws-android-sdk', open(apkfinal_path,"rb").read()):
            print ("[!] This Application use AWS_SDK")
            self.asset.exist_sdk(pkgid, True)
            logger.info(json.dumps({"step":"result","package":self.pkgid, "sdk":True}))
            pass
        else:
            print ("[!] NO AWS_SDK FOUND")
            self.asset.exist_sdk(pkgid, False)
            logger.info(json.dumps({"step":"result","package":self.pkgid, "sdk":False}))
            #os.remove(apkfinal_path)

