import os
import xml.etree.ElementTree as ET
import struct
import dex.dexparser as dexparser
import json
import subprocess
import re
import sys
import tempfile
import traceback
from zipfile import ZipFile

class DexParse:
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.tmp_dir = tempfile.TemporaryDirectory()
        
        
        self.unzip()
        self.dex_parse()

    def unzip(self):
        isdex = re.compile("classes([0-9]*).dex")
        with ZipFile(self.apk_path) as apk:
            for f in apk.namelist():
                if isdex.match(f) != None:
                    apk.extract(f, path=self.tmp_dir.name)
    def pretty(self, tt):
        JNI = {"Z":"boolean", "B":"byte","C":"char","D":"double","F":"float","I":"int","J":"long","V":"void", "S":"short"}
        if tt[0] == "L":
            return tt[1:-1].replace("/",".")
        elif tt[0] == "[":
            return tt.replace("/",".")
        else:
            if tt in JNI:
                return JNI[tt]
            else:
                if tt[:2] == "\x01L":
                    return tt[2:-1].replace("/",".")
    def dex_parse(self):
        c_list = dict()
        for dex_file in os.listdir(self.tmp_dir.name):
            print(self.tmp_dir.name+"/"+dex_file)
            d = dexparser.Dexparser(self.tmp_dir.name+"/"+dex_file)
            s_list = d.string_list()
            t_list = d.typeid_list()
            m = d.mmapdata()
            p_list = d.protoids_list()
            n_p_list = []
            for shorty_idx, return_type_idx, parameters_off in p_list:
                if parameters_off == 0:
                    param_size = 0
                else:
                    param_size = struct.unpack("<L", m[parameters_off:parameters_off+4])[0]
                params = []
                for i in range(param_size):
                    param_type_id = struct.unpack("<H", m[parameters_off+4+i*2:parameters_off+4+i*2+2])[0]
                    params.append(s_list[t_list[param_type_id]])
                n_p_list.append([s_list[t_list[return_type_idx]], params])
            m_list = d.method_list()
            for class_idx, proto_idx, name_idx in m_list:
                cls = self.pretty(str(s_list[t_list[class_idx]],"utf-8"))
                try:
                    method = str(s_list[name_idx],"utf-8")
                    if method != "clone" and method != "<clinit>":
                        if method == "<init>":
                            method = "$init"
                        proto = n_p_list[proto_idx]

                        ret = self.pretty(str(proto[0], "utf-8"))
                        params = []
                        for param in proto[1]:
                            params.append(self.pretty(str(param, "utf-8")))
                        
                        proto = [ret, params]
                        if cls in c_list:
                            if method in c_list[cls]:
                                c_list[cls][method].append(proto)
                            else:
                                c_list[cls][method] = [proto]
                        else:
                            c_list[cls] = {method:[proto]}
                except UnicodeDecodeError:
                    traceback.print_exc()
                    pass
                except Exception:
                    traceback.print_exc()
                    break
        self.names =  c_list
    def get_classes(self):
        return self.names.keys()
    def get_methods(self, class_name):
        if class_name in self.names:
            return self.names[class_name].keys()
        return None
    def get_overloads(self, class_name, method_name):
        if class_name in self.names:
            if method_name in self.names[class_name]:
                return self.names[class_name][method_name]
        return None
if __name__ == "__main__":
    dp = DexParse("../apk/com.happylabs.hps.apk")
    #dp.dex_parse()
    for cls, methods in dp.dex_parse().items():
        #print(cls)
        for method, over in methods.items():
            #print(method)
            for proto in over:
                ret = proto[0]
                params = proto[1]
                #print(ret+" ["+", ".join(params)+"]")