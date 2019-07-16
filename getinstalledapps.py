from adb.client import Client as AdbClient
from termcolor import cprint
import subprocess, os

class getInstalledApps:

    def __init__(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.adb_device = self.client.devices()[0]
        self.applist = []
        self.apppath = []
        
    def get_Applist(self):
        self.ltemp = self.adb_device.shell("pm list packages ")
        # if search_keword is none, print all lists out.
        temp = self.ltemp.split("\n")
        del temp[len(temp)-1]
        
        self.applist = [x.split(":")[1] for x in temp]
        print (self.applist)

    def get_Path(self, pkgid):

        path_temp = self.adb_device.shell("pm path " + pkgid)
        path = path_temp.split(":")[1]
        return path

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
