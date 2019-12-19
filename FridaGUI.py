import frida
from ppadb.client import Client as AdbClient
import re
import os
import traceback
import time
from dexparse import DexParse
from ScriptMaker import ScriptMaker, ScriptMaker_IOS
from assets import Assets
    
class FridaGUI:
    def __init__(self):
        print("[+] FridaGUI __init__")
        self.apk_dir = os.path.join("./apk/")
        self.js_dir = os.path.join("./static/frida_script/")
        self.serial = ""
        self.package_name = ""
        self.frida_device = ""
        self.is_ios = False
        if not os.path.exists(self.apk_dir):
            os.mkdir(self.apk_dir)
    def get_device_list(self):
        try:
            self.devices = frida.enumerate_devices()
            device_list = []
            for device in self.devices[2:]:
                device_list.append({"serial":device.id, "name":device.name, "type":device.type})
            return device_list
        except Exception as e:
            self.err = str(e)
            return None
    def get_current_device(self):
        self.frida_device = frida.get_device(self.serial)
        return {"serial":self.frida_device.id, "name":self.frida_device.name, "type":self.frida_device.type}
    def installed_list(self, serial):
        self.serial = serial
        self.adb_device = AdbClient().device(self.serial)
        p = re.compile("package:(.*)=(.*)")
        packages = []
        try:
            for pm in self.adb_device.shell("pm list packages -f").split("\n"):
                if pm == "":
                    break
                matched = p.search(pm)
                package = {"name":matched.group(2), "path":matched.group(1), "downloaded":0}
                apk_path = "%s%s.apk" % (self.apk_dir, package['name'])
                if os.path.exists(apk_path):
                    package["downloaded"] = 1
                packages.append(package)
            return packages
        except:
            traceback.print_exc()
            return []
    def apk_pull(self, pkg):
        apk_path = "%s%s.apk" % (self.apk_dir, pkg['name'])
        self.adb_device.pull(pkg['path'], apk_path)
        self.is_AWSSDK(pkg['name'])
    def get_downloaded_list(self):
        downloaded_list = []
        for f in os.listdir(self.apk_dir):
            package_name = f[:-4]
            downloaded_list.append(package_name)
        return downloaded_list
    def apk_remove(self, pkg):
        apk_path = "%s%s.apk" % (self.apk_dir, pkg)
        os.remove(apk_path)
    def get_ios_process_list(self, serial):
        print("serial", serial)
        if serial == "":
            return []
        self.serial = serial
        print("serial", self.serial)
        self.frida_device = frida.get_device(self.serial)
        if self.frida_device != "":
            process_list = []
            self.is_ios = False
            for app in self.frida_device.enumerate_processes():
                if app.pid == 1 and app.name == "launchd":
                    self.is_ios = True
                process_list.append({"name":app.name, "pid":app.pid})
            if self.is_ios:
                return process_list
            else:
                return []
        else:
            return []
    def get_dex(self, pkg):
        self.is_ios = False
        apk_path = "%s%s.apk" % (self.apk_dir, pkg)
        self.dp = DexParse(apk_path)
        return self.dp.get_classes()
    def get_classes(self, pid):
        self.pid = int(pid)
        for app in self.frida_device.enumerate_applications():
            if app.name == self.package_name:
                self.app_id = app.identifier
                break
        js = self.get_common_script("common")
        js += "\nget_classes();\n"
        classes = []
        def callback(message, data):
            if "payload" in message:
                for cls in message['payload']:
                    classes.append(cls)
                self.loaded = False
            else:
                print(message)
        self.load(self.pid, js, callback)
        return classes
    def get_methods(self, class_name):
        if self.is_ios:
            return self.get_ios_methods(class_name)
        else:
            return self.get_android_methods(class_name)
    def get_android_methods(self, class_name):
        method_names = self.dp.get_methods(class_name)
        if method_names == None:
            return None
        i = 0
        overloads = []
        for method in method_names:
            for prot in self.dp.get_overloads(class_name, method):
                overloads.append({"index":i, "method":method, "ret":prot[0], "args":", ".join(prot[1])})
                i+=1
        return overloads
    def get_ios_methods(self, cls):
        js = self.get_common_script("common")
        js += """get_methods("{0}");""".format(cls)
        methods = []
        def callback(message, data):
            if "payload" in message:
                for method in message['payload']:
                    methods.append(method)
                    print(method)
                self.loaded = False
        self.load(self.pid, js, callback)
        method_names = []
        self.method_dict = dict()
        for m in methods:
            method_names.append(m['method'])
            self.method_dict[m['method']] = m
        return method_names
    def get_frida_device(self, serial):
        self.serial = serial
        self.frida_device = frida.get_device(self.serial)
        return self.frida_device
    def get_process(self):
        if self.serial == "":
            dl = self.get_device_list()
            if len(dl) == 1:
                self.serial = dl[0]['serial']
            else:
                return None
        self.frida_device = frida.get_device(self.serial)
        print(self.frida_device)
        if self.frida_device != "":
            process_list = []
            for app in self.frida_device.enumerate_processes():
                if app.name.find(self.package_name) != -1:
                    process_list.append({"name":app.name, "pid":app.pid})
            return process_list
        else:
            return None
    def spawn(self):
        if self.is_ios:
            pid = self.frida_device.spawn([self.app_id])
            self.pid = pid
        else:
            pid = self.frida_device.spawn(self.package_name)
        for app in self.frida_device.enumerate_processes():
            if app.pid == pid:
                if app.name.find(self.package_name) == -1:
                    return {"name":self.package_name, "pid":app.pid}
                else:
                    return {"name":app.name, "pid":app.pid}
    def resume(self, pid):
        self.frida_device.resume(pid)
    
    def get_common_script(self, script_name):
        tmp_dir = self.js_dir
        if self.is_ios:
            tmp_dir += "ios/"
        else:
            tmp_dir += "android/"
        js = open(tmp_dir+script_name+".js").read()
        return js

    def get_custom_script(self, script_names):
        tmp_dir = self.js_dir+"custom/"
        js = ""
        for script_name in script_names:
            js =+ open(tmp_dir+script_name+".js").read()+"\n"
        return js
        
    def load_and_resume(self, pid, js, callback):
        js += self.get_common_script("send")
        session = self.frida_device.attach(pid)
        script = session.create_script(js)
        script.on("message", callback)
        script.load()
        self.resume(pid)
        self.loaded = True
        while self.loaded:
            pass
        script.unload()
        script.off("message", callback)
        session.detach()

    def load(self, pid, js, callback):
        js += self.get_common_script("send")
        session = self.frida_device.attach(pid)
        script = session.create_script(js)
        script.on("message", callback)
        self.loaded = True
        script.load()
        while self.loaded:
            pass
        script.unload()
        script.off("message", callback)
        session.detach()

    def get_classes_memory(self, pid):
        script = self.get_common_script("common")
        script+= "get_classes()"
        classes = []
        self.complete = False
        def callback(message, data):
            if "payload" in message:
                if message['payload'] == "complete":
                    self.complete = True
                for cls in message['payload']:
                    classes.append(cls)
        self.load(pid, script, callback)
        while True:
            if self.complete:
                break
        return classes
    
    def intercept_code(self, class_name, method):
        if self.is_ios:
            over = self.method_dict[method]
            sm = ScriptMaker_IOS(class_name, method)
            args_code = sm.arg_make(over['args'])
            ret_code = sm.ret_make(over['ret'])
            intercept = self.get_common_script("intercept")
            hook_name = "%s_%s" % (class_name, method.replace("- ","").replace("+ ","").replace(":","").replace(".",""))
            code = intercept.format(class_name, method, hook_name, args_code, ret_code)
            return code
        else:
            index = method
            methods = self.get_methods(class_name)
            over = methods[int(index)]
            sm = ScriptMaker(class_name, over['method'])
            if over['args'] != "":
                overload = ",".join("'%s'" % x for x in over['args'].strip().split(", "))
                args_code = sm.arg_make(over['args'].split(", "))
            else:
                overload = ""
                args_code = ""
            ret_code = sm.ret_make(over['ret'])

            intercept = self.get_common_script("intercept")
            code = intercept.format(class_name, over['method'], overload, args_code, ret_code)
            return code
        
    def is_AWSSDK(self, pkgid):
        asset = Assets()
        apkfinal_path = os.path.join("./apk/") + pkgid + '.apk'
        if re.search(b'(?i)aws-android-sdk', open(apkfinal_path,"rb").read()):
            if asset.exist(pkgid) == False:
                asset.add(pkgid, "", 0, "")
            asset.exist_sdk(pkgid, True)
            return True
