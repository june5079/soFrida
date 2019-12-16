var hook = new function(){
    this.init = function(){
        //hook.state = "load";
        hook.load_socket = "";
        $("#clear_button").on("click",function(){ hook.clear(); });
        hook.onclickload();
        hook.backtrace();
        hook.set_ul();
    }
    this.set_ul = function(){
        hook.ul = document.createElement("ul");
        $(hook.ul).addClass("list-group");
        $("#result_card .card-body").append(hook.ul);
    }
    this.get_info = function(){
        var process = $("#process_list .btn-secondary")[0].innerText;
        var re = /(\S+)\(([\d]+)\)/;
        var m = process.match(re);
        hook.pid = m[2];
        hook.package_name = m[1];
        hook.code = $("#code").text();
        //if(hook.state == "reload"){
            hook.unload();
            hook.clear();
        //}
    }
    this.onclickload = function(){
        $("#load_button").off().on("click",function(){
            hook.get_info();
            $.ajax({
                url:"/load",
                type:"POST",
                data: JSON.stringify({"code": hook.code, "package_name":hook.package_name, "pid":hook.pid}),
                success:function(res){
                    //hook.state = "reload";
                    $("#load_button").text("Reload");
                    $("#result_card").removeClass("d-none");
                    hook.load_result();
                }
            });
        });
        $("#spawn_button").off().on("click",function(){
            hook.get_info();
            $.ajax({
                url:"/spawn",
                type:"POST",
                data: JSON.stringify({"code": hook.code, "package_name":hook.package_name}),
                success:function(res){
                    //hook.state = "reload";
                    $("#load_button").text("Reload");
                    $("#result_card").removeClass("d-none");
                    hook.load_result();
                }
            });
        });
    }
    this.set_li = function(node){
        var li = document.createElement("li");
        $(li).addClass("list-group-item");
        $(li).html(node);
        $(hook.ul).append(li);
    }
    this.clear = function(){
        $("#result_card .card-body ul").remove()
        hook.init();
    }
    this.load_result = function(){
        hook.load_socket = io.connect("http://" + document.domain + ":" + location.port + "/load");
        hook.load_socket.on("load_result", function(msg){
            if("type" in msg){
                var tmp = "<p class='text-success'>"+msg.class+" <b>"+msg.method+"</b></p>";
                if(hook.on_backtrace()){
                    console.log(msg.backtrace);
                    tmp += "<p class='text-info'>";
                    msg.backtrace.forEach(e =>{
                        if(e.file == "native"){
                            tmp+=e.path+"("+e.file+")<br>";
                        }else{
                            tmp+=e.path+"("+e.file+":"+e.line+")<br>";
                        }
                    });
                    tmp += "</p>";
                }
                if(msg.type == "args"){
                    tmp += "<b>Arguments</b><br>";
                    msg.value.forEach(e =>{
                        var key = Object.keys(e)[0];
                        var v = e[key];
                        v = v.replace(/&/g, "&amp;");
                        v = v.replace(/</g, "&lt;");
                        v = v.replace(/>/g, "&gt;");
                        v = v.replace(/\n/g,"<br>");
                        v = v.replace(/ /g, "&nbsp");
                        v = v.replace(/\t/g, "&npsb&npsb&npsb&npsb");
                        tmp += "<span class='text-muted'>"+key+"</span> : "+v+"<br>";
                    });
                }else if(msg.type == "ret"){
                    tmp += "<b>Return</b><br>";
                    var v = msg.value.value;
                    v = v.replace(/\n/g,"<br>");
                    v = v.replace(/ /g, "&nbsp");
                    v = v.replace(/\t/g, "&npsb&npsb&npsb&npsb")
                    tmp += msg.value.type+" : "+v+"<br>";
                }
                hook.set_li(tmp);
            }else{
                hook.set_li(msg);
            }
        });
        hook.load_socket.on("load_error", function(data){
            var err = "<p class='text-danger'>";
            data.split("\n").forEach(e =>{
                err += e+"<br>";
            });
            err +="</p>";
            hook.set_li(err);
        });
    }
    this.unload = function(){
        if(hook.load_socket != "" && hook.load_socket != undefined){
            hook.load_socket.emit("script_unload");
            hook.load_socket.close();
        }
    }
    this.backtrace = function(){
        $("#backtrace_button").off().on("click", function(){
            if($(this).hasClass("btn-outline-info")){
                $(this).removeClass("btn-outline-info");
                $(this).addClass("btn-info");
            }else{
                $(this).removeClass("btn-info");
                $(this).addClass("btn-outline-info");
            }
        });
    }
    this.on_backtrace = function(){
        return $("#backtrace_button").hasClass("btn-info");
    }
}