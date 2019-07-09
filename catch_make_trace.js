function trace(className, over){
    var method = over.method;
    var index = over.index;
    var over_arg = over.args;
    var over_ret = over.ret;
    var arg_str = JSON.stringify(over_arg);
    Java.perform(function(){
        var hook = Java.use(className);
        hook[method].overloads[index].implementation = function(){
            var retval = this[method].apply(this, arguments);
            if(over_ret == "java.lang.String"){
                send(retval);
            }else if(over_ret == "java.net.URI"){
				send(String(retval));
			}
            return retval;
        }
    });
}

function uniqBy(array, key)
{
        var seen = {};
        return array.filter(function(item) {
                var k = key(item);
                return seen.hasOwnProperty(k) ? false : (seen[k] = true);
        });
}

function make_trace(cls){
    setTimeout(function() {
        Java.perform(function() {
            var hook = Java.use(cls);
            var methods = hook.class.getDeclaredMethods();
            hook.$dispose;
            var parsedMethods = [];
            methods.forEach(function(method) {
                parsedMethods.push(method.toString().replace(cls + ".", "TOKEN").match(/\sTOKEN(.*)\(/)[1]);
            });
            var targets = uniqBy(parsedMethods, JSON.stringify);
            for(var j = 0;j<targets.length;j++){
                var method = targets[j];
                var overloadCount = hook[method].overloads.length;
                for(var k = 0; k<overloadCount;k++){
                    var dic = {};
                    var arg_list = [];
                    hook[method].overloads[k].argumentTypes.forEach(function(arg){
                        arg_list.push(arg.className);
                    });
                    dic["method"] = method;
                    dic["index"] = k;
                    dic["args"] = arg_list;
                    dic["ret"] = hook[method].overloads[k].returnType.className;
                    trace(cls, dic);
                }
            }
        });
    },0);
}
Java.perform(function() {
    Java.enumerateLoadedClasses({
        onMatch: function(cls){
            cls = cls.replace("[L","").replace(";","");
            if(cls == "com.amazonaws.auth.BasicAWSCredentials"|| cls == "com.amazonaws.auth.BasicSessionCredentials" || cls == "com.amazonaws.http.HttpRequest"){
                make_trace(cls);
                send("start_trace:"+cls);
            }
        },
        onComplete: function(){
            send("search complete")
        }
    });
});

