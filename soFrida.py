import frida
import argparse
import os,sys
import subprocess
import xml.etree.ElementTree as ET
import json,time
import re
import logging
from threading import Thread
from adb.client import Client as AdbClient
from termcolor import colored, cprint
from sflogger import sfFileLogger

APKTOOL_PATH = "/usr/local/bin/apktool"

class soFrida:
    def __init__(self, pkgid, mode='usb', host=None ):
        if mode == 'usb':
            self.device = frida.get_usb_device()
            cprint("[*] USB Connected", 'green')
        elif mode == 'host':
            self.device = frida.get_device_manager().add_remote_device(host)
            cprint("[*] Host Connect", 'green')
        self.pkgid = pkgid
        self.acc_key_list = set()
        self.sec_key_list = set()
        self.session_token = set()
        self.awsregion = set()
        self.awsservice = set()
        self.awsbucket = set()
        self.key_found = False
        self.base_adb_command = ['adb']
        self.flogger = sfFileLogger(self.pkgid+".log")
        self.logger = logging.getLogger("soLogger")
        self.logger.setLevel(logging.INFO)        
        self.formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.file_handler = logging.FileHandler(self.pkgid + ".log")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.flogger.filelogger.info("[+] Vulnerable PKG_ID : " + self.pkgid)
        self.flogger.filelogger.info("[!] Logging Start")

        
        client = AdbClient(host="127.0.0.1", port=5037)
        self.adb_device = client.devices()[0]   
        self.javaperform = """
                            setTimeout(function() {
                                Java.perform(function() {
                                    %s
                                });
                            }, 0);"""
        # User can add aws service which is supported with awscli
        self.aws_servicelist = ['s3', 'lambda', 'kinesis', 'cognito', 'sns', 'dynamodb', 'simpledb']
        self.aws_regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2','ap-east-1', 'ap-south-1', 'ap-northeast-2','ap-southeast-1','ap-southeast-2','ca-central-1','cn-north-1','cn-northwest-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-north-1','sa-east-1']

    def analyze_apk(self, path):
        self.path = path
        self.dir = path[:path.rfind(".apk")]
        if os.path.exists(self.dir) == False:
            cprint("[*] Start Decode by APKTOOL", 'green')
            command = [APKTOOL_PATH, "d", "-f", "-o", self.dir, path]
            os.system(" ".join(command))
        else:
            cprint("[*] Aleady Decoded", 'red')
        self.mani = self.dir+"/AndroidManifest.xml"

        if os.path.exists(self.mani) == False:
            cprint("no manifest file", 'red')
            sys.exit(1)
        tree = ET.parse(self.mani)
        root = tree.getroot()
        self.package = ""
        for mani in root.iter("manifest"):
            self.package = mani.attrib["package"]
            break
        print("[*] PACKAGE NAME : %s" % self.package)

    def install_apk(self):
        if self.adb_device.is_installed(self.package):
            cprint("[*] Aleady Installed Package : %s" % self.package, 'yellow')
        else:
            cprint("[*] Start Install Package : %s" % self.package, 'yellow')
            self.adb_device.install(self.path)

    def uninstall_apk(self):
        cprint("[*] Start Uninstall Pakcage : %s" % self.package, 'yellow')
        self.adb_device.uninstall(self.package)
    
    def get_class_maketrace(self):
        catch_trace_js = open('catch_make_trace.js', 'r').read()
        self.trace_flag = False
        self.search_flag = True
        def trace_callback(message, data):
            if 'payload' in message:
                if message['payload'].find("start_trace:") != -1:
                    cls = message['payload'].split(":")[1]
                    cprint("[+] %s Trace Start!!" % (cls), 'yellow')
                    self.trace_flag = True
                elif message['payload'] =="search complete":
                    self.search_flag = False
                else:
                    self.findAccessKeyId(message['payload'])
            else:
                print(message['stack'])
        script = self.spwan(catch_trace_js, trace_callback)
        while self.search_flag:
            pass
        i = 1
        if self.trace_flag == False:
            cprint("[!] Switching to static mode", "yellow")
        while self.trace_flag == False:
            script.unload()
            self.search_flag = True
            script = self.run(catch_trace_js, trace_callback)
            while self.search_flag:
                pass
            i+=1
        
        while not self.key_found:
            pass
        script.unload()
        
    def spwan(self, runjs, message_callback):
        pid = self.device.spawn(self.process)
        session = self.device.attach(pid)
        script = session.create_script(runjs)
        script.on("message", message_callback)
        script.load()
        self.device.resume(pid)
        return script

    def run(self, runjs, message_callback):
        session = self.device.attach(self.process)
        script = session.create_script(runjs)
        script.on("message", message_callback)
        script.load()
        return script
    
    def findAccessKeyId (self, text):
        # Recognize AWS Key Pairs by RegEx
        regex_acc = re.compile(r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])")
        regex_sec = re.compile(r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])")

        regex_svc_A = re.compile(r"(?P<svc>[^/]+)\.(?P<region>[^.]+).amazonaws.com")
        regex_svc_B = re.compile(r"(?P<svc>[^/]+)\.amazonaws.com")
        regex_svc_C = re.compile(r"(?P<svc>[^/]+)\-(?P<region>[^.]+).amazonaws.com")    
        # https://happyrestaurant.s3.amazonaws.com/006/677/724.dat

        regex_s3case = [re.compile(r"(?P<bucket>[^/]+).s3.amazonaws.com"), re.compile(r"(?P<bucket>[^/]+).s3-(?P<region>[^.]+).amazonaws.com"), re.compile(r"s3-(?P<region>[^.]+).amazonaws.com/(?P<bucket>[^/]+)")]
        
        svc_temp = regex_svc_B.search(text)
        if svc_temp != None:
            if svc_temp.group('svc').find("s3") != -1:
                for regex_s3 in regex_s3case :
                    s3temp = regex_s3.search(text)
                    if s3temp is not None:
                        # print (text)
                        self.awsservice.add("s3")
                        self.awsbucket.add(s3temp.group('bucket'))
            else:
                svc_tempA = regex_svc_A.search(text)
                if svc_tempA != None:
                    print (text)
                    if svc_tempA.group('region').find("s3") == -1:
                        self.awsservice.add(svc_tempA.group('svc'))
                        self.awsregion.add(svc_tempA.group('region'))
                


        # if svc_temp is not No
        #         for regs3temp in regex_s3case:
        #             try:
        #                 tmp = regs3temp.search(text)
        #                 if tmp.group('bucket') is not None:
        #                     self.awsbucket.add(tmp.group('bucket'))
        #                     print (tmp.group('bucket'))
        #             except:
        #                 pass
        #     else:
        #         self.awsservice.add(svc_temp.group('svc'))



        


        # svc_tempB = regex_svc_B.search(text)
        # if svc_tempB != None:
        #     print (text)
        #     self.awsservice.add(svc_tempB.group('svc'))
        
 
 
 

        sec = regex_sec.search(text)
        if sec != None:
            #print("[*] SecretKeyId : %s" % str(sec.group()))
            self.sec_key_list.add(str(sec.group()))

        acc = regex_acc.search(text)
        if acc != None:
            #print("[*] AccessKeyId : %s" % str(acc.group()))
            self.acc_key_list.add(str(acc.group()))

        if text.endswith ("=") or text.endswith ("=="):
            self.session_token.add(text)
        
        if len(self.sec_key_list) > 0 and len(self.acc_key_list) > 0 and len(self.awsservice) > 0 and len(self.awsbucket) > 0:
            self.key_found = True

    def print_key(self):
        if len(self.acc_key_list) == 0:
            cprint("[*] No Access Key", 'red')
        else:
            cprint("[+] AccessKeyId Found", 'yellow')
            for accesskey in list(self.acc_key_list):
                cprint("\t[-] %s" % accesskey, 'green')
                subprocess.call("aws configure set aws_access_key_id %s"%accesskey, shell=True)
                self.flogger.filelogger.info("[+] AccessKeyId : " + accesskey)
                 
        if len(self.sec_key_list) == 0:
            cprint("[*] No Secret Key", 'red')
        else:
            cprint("[+] SecretKeyId Found", 'yellow')
            for secretkey in list(self.sec_key_list):
                cprint("\t[-] %s" % secretkey, 'green')
                subprocess.call("aws configure set aws_secret_access_key %s"%secretkey, shell=True)
                self.flogger.filelogger.info("[+] SecretAceessKey : " + secretkey)

    
        if len(self.session_token) == 0:
            cprint("[*] No SessionToken", 'red')
        else:
            cprint("[+] SessionToken Found", 'yellow')
            for sessiontoken in list(self.session_token):
                cprint("\t[-] %s" % sessiontoken, 'green')
                subprocess.call("aws configure set aws_session_token %s"%sessiontoken, shell=True)
                self.flogger.filelogger.info("[+] SessionToken : " + sessiontoken)

    
    def clear_logcat(self):
        adb_command = self.base_adb_command[:] 
        adb_command.append('logcat')
        adb_command.append('-c')
        try :
                
            adb_clear = subprocess.Popen(adb_command)
            # Wait for cleaning logcat
            time.sleep(1)
            cprint("[+] Logcat sucessfully cleared", 'green')
        except :
            cprint ("[!] Error occured wuth cleaning logcat",'red')
    
    def save_logcat(self, process):
        adb_command = self.base_adb_command[:]
        adb_command.append('logcat')
        adb_command.extend(['-d'])
        adb = subprocess.Popen(adb_command, stdout=subprocess.PIPE)
        adb2 = subprocess.Popen(['grep','amazonaws'], stdin=adb.stdout ,stdout=subprocess.PIPE)
        adb3 = subprocess.Popen(['grep',process], stdin=adb2.stdout ,stdout=subprocess.PIPE)
        for line in adb3.stdout.readlines():
            print (line.decode('utf-8'))
            self.flogger.filelogger.info("[Logcat] :" + line.decode('utf-8'))

    # def aws_autoconfig(self):
    #     cprint ("[*] Setting Up AWS Configuration" , "yellow")
    #     subprocess.call("aws configure set %s %s"%key %value, shell=True) 
                    
    def remove_dir(self):
        cprint("[*] Remove Apktool Dirctory", 'green')
        command = ["rm", "-rf", self.dir]
        os.system(" ".join(command))
    
    # Recognize what aws service is used for app
    # def aws_finder(self):
    #     with open(self.pkgid + '.log', 'r') as flog:
    #         flog_list = flog.readlines()
    #         for flog_line in flog_list:
    #             # print (flog_line)
    #             for r in self.aws_regions:
    #                 if r in flog_line:
    #                     self.awsregion.add(r)
    #                 else:
    #                     pass
            
    #             for s in self.aws_servicelist:
    #                 if s in flog_line:
    #                     self.awsservice.add(s)
    #                 else:
    #                     pass
    #         self.flogger.filelogger.info(self.awsregion)
    #         self.flogger.filelogger.info(self.awsservice)
    
    # def bucket_finder(self, logfile):

    #     regex_list = []
    #     # regex_list.append(re.compile(r"?P<bucket>[^/]+).s3.amazonaws.com"))
    #     # regex_list.append(re.compile(r"?P<bucket>[^/]+).s3-(?P<region>[^.]+).amazonaws.com"))
    #     # regex_list.append(re.compile(r"s3-(?P<region>[^.]+).amazonaws.com/(?P<bucket>[^/]+)"))
    #     caseA = re.compile(r"for\s(?P<bucket>[^/]+).s3.amazonaws.com")
    #     caseB = re.compile(r"for\s(?P<bucket>[^/]+).s3-(?P<region>[^.]+).amazonaws.com")
    #     caseC = re.compile(r"for\ss3-(?P<region>[^.]+).amazonaws.com/(?P<bucket>[^/]+)")
    #     regex_list.append(caseA)
    #     regex_list.append(caseB)
    #     regex_list.append(caseC)
        
    #     with open (logfile, "r") as flog:
    #         flog_list = flog.readlines()
            
    #         # for rex in regex_list:
    #         for flog in flog_list:
    #             for rextest in regex_list:
    #                 try:
    #                     matchobj = rextest.search(str(flog))
    #                     if matchobj:
    #                         print (matchobj.group("bucket"))
    #                         print (matchobj.group("region"))
    #                 except:
    #                     pass

                # if matchobj.group("bucket") is not None:
                #     self.awsbucket.add(matchobj.group("bucket"))
                #     print (matchobj.group("bucket"))
                # if matchobj.group("region") is not None:
                #     self.awsregion.add(matchobj.group("region"))

        # print (matchobj.group("bucket"))

            # for regex in regex_list:
            #     for flog in flog_list:
            #         matchobj = regex.search(flog)

        # print (self.awsregion + " : " + self.awsbucket)

ap = argparse.ArgumentParser(description='Test APIBleed vulnerability - cloud backend - not for testing general mobile vulnerability.')
ap.add_argument('-t', '--target', dest='target', required=False, help='apk file path')
ap.add_argument('-p', '--process', dest='process', required=False, help='Prcess Nmae')
ap.add_argument('-U', '--usb', action='store_true')
ap.add_argument('-H', '--host', dest='host', nargs='?', default='', required=False)

args = ap.parse_args()

if args.usb and args.host == None:
    cprint("Usage : %s -U -t [target] or %s -H [frida_listen_ip] -t [target]" % (sys.argv[0], sys.argv[0]), 'red')
elif args.usb:
    sf = soFrida(args.process, 'usb' )
elif args.H != None:
    sf = soFrida('host', args.host)

# Clear Logcat
sf.clear_logcat()
time.sleep(1)
sf.process = args.process
sf.get_class_maketrace()
sf.print_key()
sf.save_logcat(args.process)
cprint ("[+] Done")
# sf.aws_finder()
# sf.bucket_finder(args.process+".log")

print (sf.awsservice)
print (sf.awsbucket)
