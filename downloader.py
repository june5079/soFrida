from gpapi.googleplay import GooglePlayAPI, RequestError

import sys, os, time
import traceback
import argparse
import subprocess

class Downloader:

    def __init__ (self, gid, gpw):
        self.gid = gid
        self.gpw = gpw

        ff = "/Users/janeblack/Downloads/googleplay-api/a2.txt"
        apkfile_path = os.path.join("/Users/janeblack/Downloads/apk/")

        # LOGIN
        server = GooglePlayAPI('ko_KR', 'Asia/Seoul')
        print('\nLogging in with email and password\n')
        server.login(self.gid, self.gpw, None, None)
        gsfId = server.gsfId
        authSubToken = server.authSubToken
        print(authSubToken)

        print('\nNow trying secondary login with ac2dm token and gsfId saved\n')
        server = GooglePlayAPI('ko_KR', 'Asia/Seoul')
        server.login(None, None, gsfId, authSubToken)

        # READ FROM FILES
        f = open(ff, 'r')
        downlist = f.readlines()

        # DOWNLOAD
        for x in downlist :
            docid = x.strip("\n")
            print('\nAttempting to download %s\n' % docid)
            try:
                fl = server.download(docid)
                with open(apkfile_path + docid + '.apk', 'wb') as apk_file:
                    for chunk in fl.get('file').get('data'):
                        apk_file.write(chunk)
                    print('\nDownload successful\n')

            except :
                print("Unexpected error:", sys.exc_info()[0])
                traceback.print_exc()
                #time.sleep(3)
                pass

            time.sleep(1)

