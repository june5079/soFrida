function get_classes(){
    send(Object.keys(ObjC.classes));
}
function get_methods(cls){
    var method_list = [];
    var methods = ObjC.classes[cls].$methods;
    for(var i = 0;i<methods.length;i++){
        var dict = {};
        dict.method = methods[i];
        dict.args = ObjC.classes[cls][dict.method].argumentTypes;
        dict.ret = ObjC.classes[cls][dict.method].returnType;
        method_list.push(dict);
    }
    send(method_list);
}