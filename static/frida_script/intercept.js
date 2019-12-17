Java.perform(function(){{
    var cls = Java.use("{0}");
    var method = cls["{1}"].overload({2});
    method.implementation = function(){{
{3}
        var retval = this["{1}"].apply(this, arguments);
{4}
        return retval;
    }};
}});