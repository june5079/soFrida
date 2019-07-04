from gpapi.googleplay import GooglePlayAPI, RequestError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import sys, os, time
import traceback
import argparse
import subprocess

class Downloader:

    def __init__ (self, gid, gpw, pkgid):
        self.gid = gid
        self.gpw = gpw
        self.pkgid = pkgid
        self.options = Options()
        self.options.headless = False
        self.browser = webdriver.Chrome('./chromedriver', chrome_options=self.options)
        self.request_url = "https://accounts.google.com/b/0/DisplayUnlockCaptcha"

        self.apkfile_path = os.path.join("/tmp/")
        self.server = GooglePlayAPI('ko_KR', 'Asia/Seoul')

        # LOGIN
    def firstlogin(self):
        try:
            print('\nLogging in with email and password\n')
            self.server.login(self.gid, self.gpw, None, None)
            self.gsfId = self.server.gsfId
            self.authSubToken = self.server.authSubToken
            print("[+] Token is : " + self.authSubToken)
            self.secondlogin()

        except:
            traceback.print_exc()
            print ("Need to unlock account")
            self.browser.get(self.request_url)
            # self.browser.find_element_by_css_selector("#submitChallenge").click()
            val = input("Recall firstlogin")
            self.browser.close()
            self.firstlogin()

    def secondlogin(self):
        print('\nNow trying secondary login with ac2dm token and gsfId saved\n')
        self.server = GooglePlayAPI('ko_KR', 'Asia/Seoul')
        self.server.login(None, None, self.gsfId, self.authSubToken)

        # call DOWNLOAD
        self.startdownload()

    def startdownload(self):
        print('\nAttempting to download %s\n' % self.pkgid)
        try:
            fl = self.server.download(self.pkgid)
            with open(self.apkfile_path + self.pkgid + '.apk', 'wb') as apk_file:
                for chunk in fl.get('file').get('data'):
                    apk_file.write(chunk)
                print('\nDownload successful\n')

        except :
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
            #time.sleep(3)
            pass

        # time.sleep(1)

