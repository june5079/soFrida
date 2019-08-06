from assets import Assets
from adb.client import Client as AdbClient
from termcolor import cprint
import subprocess, os, re

class getInstalledApps:

    def __init__(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.adb_device = self.client.devices()[0]
        self.applist = []
        self.apppath = []
        self.asset = Assets()
        
    def get_Applist(self):
        self.ltemp = self.adb_device.shell("pm list packages ")
        # if search_keword is none, print all lists out.
        temp = self.ltemp.split("\n")
        del temp[len(temp)-1]
        
        self.applist = [x.split(":")[1] for x in temp]
        #print (self.applist)
        return self.applist

    def get_Path(self, pkgid):
        path_temp = self.adb_device.shell("pm path " + pkgid)
        path = path_temp.split(":")[1].strip()
        return path

    def get_app(self, pkgid):
        path = self.get_Path(pkgid)
        tmp_path = os.path.join("./tmp/") + pkgid + '.apk'
        data = self.adb_device.pull(path, tmp_path)
        if self.asset.exist(pkgid) == False:
            self.asset.add(pkgid, "", 0, "")

    def get_SDKApps(self, pkgid):
        apkpath = str(self.get_Path(pkgid))
        apkfinal_path = str("tmp/" + pkgid + ".apk")
            
        self.adb_device.pull(apkpath.strip("\n"), apkfinal_path)

        cprint('[+] Checking AWS_SDK', 'blue')

        s = os.popen('/usr/bin/grep -i "aws-android-sdk" {0}'.format(apkfinal_path)).read()
        if 'matches' in s:
            cprint ("[!] This Application use AWS_SDK", 'blue')
            pass
        else:
            cprint ("[!] NO AWS_SDK FOUND", 'blue')
            os.remove(apkfinal_path)
    def is_AWSSDK(self, pkgid):
        apkfinal_path = os.path.join("./tmp/") + pkgid + '.apk'
        if re.search(b'(?i)aws-android-sdk', open(apkfinal_path,"rb").read()):
            self.asset.exist_sdk(pkgid, True)
            return True
        else:
            self.asset.exist_sdk(pkgid, False)
            return False