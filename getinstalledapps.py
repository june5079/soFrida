from adb.client import Client as AdbClient
from multiprocessing import Pool
import time
import os


class getInstalledApps:

    def __init__(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.adb_device = self.client.devices()[0]
        self.applist = []
        self.apppath = []
        self.ltemp = self.adb_device.shell("pm list packages")
        self.applist = self.ltemp.split("\n")
        # time.sleep(3)

        with Pool(16) as p:
            p.map(self.get_Path, self.applist)

    def get_Path(self, applist):
        while applist:
            try:
                ptemp = self.adb_device.shell("pm path "+ (applist.pop(0)).split(":")[1])
                print (ptemp)
                self.apppath.append(ptemp)
            except:
                pass
            
        print (self.apppath)
    
    def get_SDKApps(self):
        
        for apk in self.apppath:
            self.adb_device.pull(str(apk).split(":")[1], "tmp/installed/"+str(apk).split(":")[1]+".apk")
            apkfinal_path = "tmp/installed/"+apk+".apk"

            print('[+] Checking AWS_SDK')

            
            s = os.popen('/usr/bin/grep -i "aws-android-sdk" {0}'.format(apkfinal_path)).read()
            if 'matches' in s:
                print ("[!] This Application use AWS_SDK")
                pass
            else:
                print ("[!] NO AWS_SDK FOUND")
                os.remove(apkfinal_path)



    

