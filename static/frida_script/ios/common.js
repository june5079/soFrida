function trace(pattern)
{
	var res = new ApiResolver("objc");
	var matches = res.enumerateMatchesSync(pattern);
	var targets = uniqBy(matches, JSON.stringify);

	return targets;
}
// remove duplicates from array
function uniqBy(array, key) 
{
	var seen = {};
	return array.filter(function(item) {
		var k = key(item);
		return seen.hasOwnProperty(k) ? false : (seen[k] = true);
	});
}
function get_classes(){
    send(Object.keys(ObjC.classes));
}
function get_methods(cls){
    var method_list = [];
    var methods = trace("*["+cls+" *]");
    console.log(methods);
    methods.forEach(function(method) {
        console.log(JSON.stringify(method));
        //console.log(ObjC.classes[cls][method.name].argumentTypes);
        //console.log(ObjC.classes[cls][method.name].returnType);
	});
    /*
    for(var i = 0;i<methods.length;i++){
        var dict = {};
        dict.method = methods[i];
        dict.args = ObjC.classes[cls][dict.method].argumentTypes;
        dict.ret = ObjC.classes[cls][dict.method].returnType;
        method_list.push(dict);
    }*/
    //send(method_list);
    //console.log(method_list);
}
get_methods("SMJailBreak");