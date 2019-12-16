import frida
from adb.client import Client as AdbClient
import re
import os
import traceback
import time
from dexparse import DexParse
from ScriptMaker import ScriptMaker
    
class FridaGUI:
    def __init__(self):
        print("[+] FridaGUI __init__")
        self.apk_dir = os.path.join("./apk/")
        self.js_dir = os.path.join("./static/frida_script/")
        self.serial = ""
        self.package_name = ""
        self.frida_device = ""
        if not os.path.exists(self.apk_dir):
            os.mkdir(self.apk_dir)
    def get_device_list(self):
        try:
            self.devices = AdbClient().devices()
            device_list = []
            for device in self.devices:
                device_list.append({"serial":device.serial, "status":device.get_state()})
            return device_list
        except Exception as e:
            self.err = str(e)
            return None
    def get_current_device(self):
        print("GET CURRENT DEVICE!!!!!!!!!")
        self.device = AdbClient().device(self.serial)
        return {"serial":self.device.serial, "status":self.device.get_state()}
    def installed_list(self, serial):
        self.serial = serial
        self.device = AdbClient().device(self.serial)
        p = re.compile("package:(.*)=(.*)")
        packages = []
        try:
            for pm in self.device.shell("pm list packages -f").split("\n"):
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
        self.device.pull(pkg['path'], apk_path)
    def get_downloaded_list(self):
        downloaded_list = []
        for f in os.listdir(self.apk_dir):
            package_name = f[:-4]
            downloaded_list.append(package_name)
        return downloaded_list
    def apk_remove(self, pkg):
        apk_path = "%s%s.apk" % (self.apk_dir, pkg)
        print(apk_path)
        os.remove(apk_path)
    def get_dex(self, pkg):
        apk_path = "%s%s.apk" % (self.apk_dir, pkg)
        self.dp = DexParse(apk_path)
        return self.dp.get_classes()
    def get_methods(self, class_name):
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
    def get_frida_device(self, serial):
        self.serial = serial
        self.device = frida.get_device(self.serial)
        return self.device
    def get_process(self):
        print(self.serial)
        print(self.frida_device)
        if self.frida_device == "" and self.serial != "":
            print(self.serial)
            self.frida_device = frida.get_device(self.serial)
        print(self.frida_device)
        if self.frida_device != "":
            process_list = []
            for app in self.frida_device.enumerate_processes():
                if app.name.find(self.package_name) != -1:
                    process_list.append({"name":app.name, "pid":app.pid})
            print(process_list)
            return process_list
        else:
            print("NO!!!!!NONE!!!!")
            return None
    def spawn(self):
        pid = self.frida_device.spawn(self.package_name)
        #session = self.frida_device.attach(pid)
        for app in self.frida_device.enumerate_processes():
            if app.pid == pid:
                print(app.name)
                if app.name.find(self.package_name) == -1:
                    return {"name":self.package_name, "pid":app.pid}
                else:
                    return {"name":app.name, "pid":app.pid}
    def resume(self, pid):
        self.frida_device.resume(pid)
        
    def load_and_resume(self, pid, js, callback):
        js = js+"\n"+open(self.js_dir+"send.js").read()
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
        js = js+"\n"+open(self.js_dir+"send.js").read()
        session = self.frida_device.attach(pid)
        script = session.create_script(js)
        script.on("message", callback)
        script.load()
        self.loaded = True
        while self.loaded:
            pass
        script.unload()
        script.off("message", callback)
        session.detach()

    def get_classes_memory(self, pid):
        script = open("./static/frida_script/common.js","r").read()
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
    
    def intercept_code(self, class_name, index):
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

        intercept = open(self.js_dir+"intercept.js").read()
        code = intercept.format(class_name, over['method'], overload, args_code, ret_code)
        return code
        