function send_arg(cls, method, args, context){
    var bt = backtrace(context);
    send({"type":"args", "value":args, "class":cls, "method":method, "backtrace":bt, "os":"ios"}); 
}
function send_ret(cls, method, type, value, context){
    var bt = backtrace(context);
    send({"type":"ret", "value":{"type":type, "value":value}, "class":cls, "method":method, "backtrace":bt, "os":"ios"});
}
function backtrace(context){
    return Thread.backtrace(context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress);
}