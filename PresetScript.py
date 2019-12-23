import os.path
import os

class PresetScript:
    def __init__(self):
        self.dir = os.path.join("./scripts/")
        
    def saved_list(self):
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        
        s_list = []
        for f in os.listdir(self.dir):
            print(f)
            if os.path.isfile(self.dir+f):
                s_list.append(f)
                print(f)
        
        return s_list
    def check_name(self, name):
        if name[-3:] != ".js":
            name += ".js"
        if os.path.exists(self.dir+name):
            self.msg = "name exist"
            return False
        else:
            return True
    
    def save(self, code, name):
        if name[-3:] != ".js":
            name += ".js"
        try:
            with open(self.dir+name, "w") as f:
                f.write(code)
            return True
        except Exception as e:
            self.msg = str(e)
            return False
        