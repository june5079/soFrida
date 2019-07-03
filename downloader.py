from gpapi.googleplay import GooglePlayAPI, RequestError

import sys, os, time
import traceback
import argparse
import subprocess

class Downloader:

    def __init__ (self, gid, gpw, pkgid):
        self.gid = gid
        self.gpw = gpw
        self.pkgid = pkgid

        apkfile_path = os.path.join("/tmp/")

        # LOGIN
        server = GooglePlayAPI('ko_KR', 'Asia/Seoul')
        print('\nLogging in with email and password\n')
        server.login(self.gid, self.gpw, None, None)
        gsfId = server.gsfId
        authSubToken = server.authSubToken
        print("[+] Token is : " + authSubToken)

        print('\nNow trying secondary login with ac2dm token and gsfId saved\n')
        server = GooglePlayAPI('ko_KR', 'Asia/Seoul')
        server.login(None, None, gsfId, authSubToken)

        # DOWNLOAD

        print('\nAttempting to download %s\n' % self.pkgid)
        try:
            fl = server.download(self.pkgid)
            with open(apkfile_path + self.pkgid + '.apk', 'wb') as apk_file:
                for chunk in fl.get('file').get('data'):
                    apk_file.write(chunk)
                print('\nDownload successful\n')

        except :
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
            #time.sleep(3)
            pass

        # time.sleep(1)

