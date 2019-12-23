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
    var classes = Object.keys(ObjC.classes);
    send(classes);
}
function get_methods(cls){
    var method_list = [];
    var methods = trace("*["+cls+" *]");
    methods.forEach(function(method) {
        var matched = method.name.match(/([+-]+)\[(.*) (.*)\]/);
        var method_name = matched[1]+" "+matched[3];
        var dict = {};
        dict.method = method_name;
        dict.args = ObjC.classes[cls][dict.method].argumentTypes;
        dict.ret = ObjC.classes[cls][dict.method].returnType;
        method_list.push(dict);
    });
    send(method_list);
}