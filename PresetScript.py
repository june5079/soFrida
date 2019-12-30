import os.path
import os
import re

class PresetScript:
    def __init__(self):
        self.dir = os.path.join("./scripts/")
        self.saved_file_list = []
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        
        for f in os.listdir(self.dir):
            if os.path.isfile(self.dir+f):
                self.saved_file_list.append({"name":f, "setted":False})
        
    def saved_list(self):
        return self.saved_file_list
    def check_name(self, name):
        if name[-3:] != ".js":
            name += ".js"

        for sf in self.saved_file_list:
            if sf['name'] == name:
                self.msg = "File exists!"
                return False
        return True
    
    def save(self, code, name, overwrite):
        if name[-3:] != ".js":
            name += ".js"
        try:
            with open(self.dir+name, "w") as f:
                f.write(code)
                if not overwrite:
                    self.saved_file_list.append({"name":name, "setted":False})
            return True
        except Exception as e:
            self.msg = str(e)
            return False
    
    def search(self, text):
        searched = []
        for sf in self.saved_file_list:
            with open(self.dir+sf['name'], "r") as s:
                if re.match(".*"+text+".*", s.read().replace("\n",""), re.IGNORECASE):
                    searched.append(sf)
        return searched
    
    def set_script(self, name, doset):
        for sf in self.saved_file_list:
            if sf["name"] == name:
                sf["setted"] = doset
                return True
        return False

    def get_setted_code(self):
        code = ""
        for sf in self.saved_file_list:
            if sf["setted"]:
                with open(self.dir+sf["name"], "r") as f:
                    code += f.read()+"\n"
        return code

    def delete_script(self, name):
        for sf in self.saved_file_list:
            if sf["name"] == name:
                os.remove(self.dir+sf["name"])
                self.saved_file_list.remove(sf)
                return True
        return False

    def view_script(self, name):
        for sf in self.saved_file_list:
            if sf["name"] == name:
                with open(self.dir+sf["name"], "r") as f:
                    return f.read()
        return None