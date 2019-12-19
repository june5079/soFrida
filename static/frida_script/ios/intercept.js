var {2} = ObjC.classes["{0}"]["{1}"];
Interceptor.attach({2}.implementation, {{
	onEnter: function(args){{
{3}
	}},
	onLeave: function(retval){{
{4}
	}}
}});