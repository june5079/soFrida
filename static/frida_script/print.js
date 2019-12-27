function uniqBy(array, key)
{
    var seen = {};
    return array.filter(function(item) {
        var k = key(item);
        return seen.hasOwnProperty(k) ? false : (seen[k] = true);
    });
}
function trim(s){
    return ( s || '' ).replace( /^\s+|\s+$/g, '' );
}
function caller_json(caller){
    var re = /(\S+)\(([\S\s]+)\)/;
    var matches = caller.match(re);
    if(matches){
        var method_path = matches[1];
        var file_name = matches[2];
        var names = file_name.split(":");
        var json = {"path":method_path};
        if(names.length == 2){
            json.file = names[0];
            json.line = parseInt(names[1]);
        }else{
            json.file = "native";
        }
        return json;
    }else{
        return null;
    }
}
function backtrace(){
    var backtrace = [];
	Java.perform(function(){
        try{
            var bt = Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new());
            var callers = bt.split("at ");
            for(var i = 1;i<callers.length;i++){
                var caller = trim(callers[i]);
                backtrace.push(caller_json(caller));
            }
        }catch(e){
            backtrace = null;
        }
    });
    return backtrace;
}
function caller_equal(bt, data){
    var caller = bt[1];
    var target = caller_json(data);
    if(target != null){
        if(caller.path != target.path) return false;
        if(caller.file != target.file) return false;
        if(target.file != "native"){
            if(caller.line != target.line) return false;
        }
        return true;
    }else{
        return false;
    }

}
function printarg(method, arg){
    var arg_result = [];
    var types = method.argumentTypes;
    for(var i=0; i<types.length; i++){
        arg_result.push(print(types[i].className, arg[i]));
    }
    return arg_result;
}
function printret(method, ret){
    return print(method.returnType.className, ret);
}
function type_printable(type, value){
    
}
function print(data){
    send({"bold":data})
}
/*
function print(type, value){
    var result = {"type":type, "value":null};
    if(type == "[B"){
        try{
            Java.perform(function(){
            result.value = Java.use("java.lang.String").$new(value).toString();
            });
        }catch(e){
            result.value = value;
        }
    }else if(type == "java.util.List"){
        var list = [];
		if(value != null){
			for(var i = 0;i<value.size();i++){
                list.push(String(value.get(i)));
            }
            result.value = list;
        }
	}else if(type == "java.util.Map" || type == "android.os.Bundle" ){
		if(value != null){
            var json = {};
			var iter = value.keySet().iterator();
			while(iter.hasNext()){
                var key = iter.next();
                json[key] = value.get(key);
            }
            result.value = json;
        }
    }else if(type == "void"){
        result.value = null;
    }else{
        result.value = String(value);
    }
    return result;
}*/
function simple_hook(class_name, method){
    Java.perform(function(){
        var cls = Java.use(class_name);
        var overloads = cls[method].overloads;
        overloads.forEach(function(hook){
			var overload = [];
			hook.argumentTypes.forEach(function(e){
				overload.push(e.className);
			});
			var result = "[*] TRACE START : "+class_name+" "+method+"("+overload.join(", ")+")";
			send({"args":null, "ret":null, "bt":null, "user":result});
            hook.implementation = function(){
                var arg_val = printarg(hook, arguments);
                var bt = backtrace();
                var retval = this[method].apply(this, arguments);
                var ret_val = printret(hook, retval);
                send({"class":class_name, "method":method, "args":arg_val, "ret":ret_val, "bt":bt, "user":null});
                return retval;
            };
        })
    });
};
function echo(data){
    send({"class":null, "method":null, "args":null, "ret":null, "bt":null, "user":data});
};