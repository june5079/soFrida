function send_arg(cls, method, args){
    var bt = backtrace();
    send({"type":"args", "value":args, "class":cls, "method":method, "backtrace":bt, "os":"android"}); 
}
function send_ret(cls, method, type, value){
    var bt = backtrace();
    send({"type":"ret", "value":{"type":type, "value":value}, "class":cls, "method":method, "backtrace":bt, "os":"android"});
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
            var Log = Java.use("android.util.Log");
            var bt = Log.getStackTraceString(Java.use("java.lang.Exception").$new());
            var callers = bt.split("at ");
            for(var i = 1;i<callers.length;i++){
                var caller = trim(callers[i]);
                backtrace.push(caller_json(caller));
            }
        }catch(e){
            console.log(e);
            backtrace = [];
        }
    });
    return backtrace;
}