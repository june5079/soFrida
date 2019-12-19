class ScriptMaker:
    tab = "\t"*2
    def __init__(self, cls, method):
        self.cls = cls
        self.method = method

    def arg_make(self, args):
        arg_code = ""
        if len(args) != 0:
            arg_code += self.tab+"var p=[];\n"
            i = 0
            for arg in args:
                print(arg)
                arg_code += self.arg_types(arg)(i, arg)
                i+=1
            arg_code += self.tab+self.send_arg()+"\n"
        return arg_code
    def ret_make(self, ret):
        return self.tab+self.ret_types(ret)(ret)+"\n"

    def arg_types(self, arg_type):
        if "java.lang.String" == arg_type:
            return self.arg_string
        elif arg_type in ["java.util.List", "java.util.ArrayList"]:
            return self.arg_list
        elif arg_type in ["java.util.Map", "java.util.HashMap", "android.os.Bundle"]:
            return self.arg_map
        elif arg_type in ["[B"]:
            return self.arg_bytearray
        else:
            return self.arg_force_string
    def ret_types(self, ret_type):
        if "java.lang.String" == ret_type:
            return self.ret_string
        elif "void" == ret_type:
            return self.ret_void
        elif ret_type in ["java.util.List", "java.util.ArrayList"]:
            return self.ret_list
        elif ret_type in ["java.util.Map", "java.util.HashMap", "android.os.Bundle"]:
            return self.ret_map
        elif ret_type in ["[B"]:
            return self.ret_bytearray
        else:
            return self.ret_force_string
    
    def arg_string(self, index, t):
        code = self.tab+"""p.push({{"{0}": arguments[{1}]}});\n""".format(t, index)
        return code

    def arg_force_string(self, index, t):
        code = self.tab+"""p.push({{"{0}": String(arguments[{1}])}});\n""".format(t, index)
        return code

    def arg_list(self, index, t):
        code = """if(arguments[{0}] != null){{
    var p_{0} = [];
    for(var i = 0;i<arguments[{0}].size();i++){{
        p_{0}.push(String(arguments[{0}].get(i)));
    }}
    p.push({{"{1}":p_{0}}});
}}else{{
    p.push({{"{1}":"null"}});
}}""".format(index, t)
        code = "\n".join(self.tab+x for x in code.split("\n"))+"\n"
        return code
    
    def ret_list(self, t):
        code = """if(retval != null){{
    var r = [];
    for(var i = 0;i<retval.size();i++){{
        r.push(String(retval.get(i)));
    }}
    send_ret("{1}","{2}","{0}",r);
}}else{{
    send_ret("{1}","{2}","{0}","null");
}}""".format(t, self.cls, self.method)
        code = "\n".join(self.tab+x for x in code.split("\n"))+"\n"
        return code

    def arg_map(self, index, t):
        code = """if(arguments[{0}] != null){{
    var json = {{}};
    var iter = arguments[{0}].keySet().iterator();
    while(iter.hasNext()){{
        var key = iter.next();
        json[key] = String(arguments[{0}].get(key));
    }}
    p.push({{"{1}":JSON.stringify(json)}});
}}else{{
    p.push({{"{1}":"null"}});
}}""".format(index, t)
        code = "\n".join(self.tab+x for x in code.split("\n"))+"\n"
        return code

    def ret_map(self, t):
        code = """if(retval != null){{
    var json = {{}};
    var iter = retval.keySet().iterator();
    while(iter.hasNext()){{
        var key = iter.next();
        json[key] = String(retval.get(key));
    }}
    send_ret("{1}","{2}","{0}",json);
}}else{{
    send_ret("{1}","{2}","{0}","null");
}}""".format(t, self.cls, self.method)
        code = "\n".join(self.tab+x for x in code.split("\n"))+"\n"
        return code
    
    def arg_bytearray(self, index, t):
        code = """if(arguments[{0}] != null){{
    var p_{0} = Memory.alloc(arguments[{0}].length);
    var arr_{0} = [];
    for(var i = 0;i<arguments[{0}].length;i++){{
        arr_{0}.push(arguments[{0}][i]);
    }}
    p_{0}.writeByteArray(arr_{0});
    p.push({{"{1}":"\\n"+hexdump(p_{0},{{length: arguments[{0}].length}})}});
}}else{{
    p.push({{"{1}":"null"}});
}}""".format(index, t)
        code = "\n".join(self.tab+x for x in code.split("\n"))+"\n"
        return code

    def ret_bytearray(self, t):
        code = """if(retval != null){{
    var r = Memory.alloc(retval.length);
    var arr = [];
    for(var i = 0;i<retval.length;i++){{
        arr.push(retval[i]);
    }}
    r.writeByteArray(arr);
    send_ret("{1}","{2}","{0}","\\n"+hexdump(r,{{length: retval.length}}));
}}else{{
    send_ret("{1}","{2}","{0}","null");
}}""".format(t, self.cls, self.method)
        code = "\n".join(self.tab+x for x in code.split("\n"))+"\n"
        return code
    
    def send_arg(self):
        code = """send_arg("{0}", "{1}", p);""".format(self.cls, self.method)
        return code

    def ret_string(self, t):
        code = """send_ret("{1}","{2}","{0}",retval);""".format(t, self.cls, self.method)
        return code

    def ret_force_string(self, t):
        code = """send_ret("{1}","{2}","{0}",String(retval));""".format(t, self.cls, self.method)
        return code

    def ret_void(self, t):
        return ""

class ScriptMaker_IOS:
    tab = "\t"*2
    def __init__(self, cls, method):
        self.cls = cls
        self.method = method

    def arg_make(self, args):
        arg_code = ""
        if len(args) != 0:
            if len(args) > 2:
                arg_code += self.tab+"var p=[];\n"
            i = 0
            for arg in args:
                if i > 1:
                    arg_code += self.arg_types(arg)(i, arg)
                i+=1
            if len(args) > 2:
                arg_code += self.tab+self.send_arg()
        return arg_code
    def ret_make(self, ret):
        return self.tab+self.ret_types(ret)(ret)

    def arg_types(self, arg_type):
        if arg_type in ["pointer"]:
            return self.arg_pointer
        else:
            return self.arg_force_object
    def ret_types(self, ret_type):
        if ret_type in ["pointer"]:
            return self.ret_pointer
        elif ret_type == "void":
            return self.ret_void
        else:
            return self.ret_force_object
    
    def arg_pointer(self, index, t):
        code = """p.push({{"{0}": (new ObjC.Object(args[{1}])).toString()}});""".format(t, index)
        code = "\n".join(self.tab+x for x in code.split("\n"))+"\n"
        return code

    def arg_force_object(self, index, t):
        code = self.tab+"""p.push({{"{0}": args[{1}]}});\n""".format(t, index)
        return code

    def send_arg(self):
        code = """send_arg("{0}", "{1}", p, this.context);""".format(self.cls, self.method)
        return code

    def ret_pointer(self, t):
        code = """send_ret("{1}","{2}","{0}", (new ObjC.Object(retval)).toString(), this.context);""".format(t, self.cls, self.method)
        return code

    def ret_force_object(self, t):
        code = self.tab+"""send_ret("{1}","{2}","{0}", retval, this.context);\n""".format(t, self.cls, self.method)
        return code

    def ret_void(self, t):
        return ""