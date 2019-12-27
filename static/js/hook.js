var hook = new function(){
    this.init = function(){
        //hook.state = "load";
        hook.load_socket = "";
        $("#clear_button").on("click",function(){ hook.clear(); });
        hook.onclickload();
        hook.backtrace();
        hook.scripts();
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
        hook.code = hook.code_editor.getValue();
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
    this.content_search_form = function(){
        $("#presetModal #search_form").off().on("keyup", function(e){
            if(e.keyCode == 13){
                var search_text = $(this).val();
                $.ajax({
                    url:"/content_search",
                    type:"POST",
                    data: JSON.stringify({"text": search_text}),
                    success: function(res){
                        $("#presetModal tbody").html(res);
                    }
                });
            }
        });
    }
    this.set_click = function(){
        $("#presetModal .set").off().on("click",function(){
            var button = $(this);
            $.ajax({
                url:"/set_script",
                type:"POST",
                data:JSON.stringify({"name": $(this).parents("tr").children()[0].innerText, "doset":true}),
                success:function(res){
                    if(res.result == "success"){
                        button.removeClass("btn-outline-info set");
                        button.addClass("btn-info setted");
                        button.text("SETTED");
                        hook.setted_click();
                    }else{
                        alert("fail set script");
                    }
                }
            });
        });   
    }
    this.setted_click = function(){
        $("#presetModal .setted").off().on("click",function(){
            var button = $(this);
            $.ajax({
                url:"/set_script",
                type:"POST",
                data:JSON.stringify({"name": $(this).parents("tr").children()[0].innerText, "doset":false}),
                success:function(res){
                    if(res.result == "success"){
                        button.removeClass("btn-info setted");
                        button.addClass("btn-outline-info set");
                        button.text("SET");
                        hook.set_click();
                    }else{
                        alert("fail set script");
                    }
                }
            });
        });
    }
    this.delete_click = function(){
        $("#presetModal .delete").off().on("click",function(){
            var button = $(this);
            $.ajax({
                url:"/delete_script",
                type:"POST",
                data:JSON.stringify({"name": $(this).parents("tr").children()[0].innerText}),
                success:function(res){
                    if(res.result == "success"){
                        button.parents("tr").remove();
                    }else{
                        alert("fail delete script");
                    }
                }
            });
        });
    }
    this.view_click = function(){
        $("#presetModal .view").off().on("click",function(){
            var button = $(this);
            var name = $(this).parents("tr").children()[0].innerText;
            $.ajax({
                url:"/view_script",
                type:"POST",
                data:JSON.stringify({"name": name}),
                success:function(res){
                    if(res.result == "success"){
                        hook.view_script.setValue(res.code);
                        hook.view_script.gotoLine(1);
                        $("#viewModal h5").text(name);
                        $("#viewModal").modal();
                    }else{
                        alert("fail view script");
                    }
                }
            });
        });
        $("#edit_save_button").off().on("click",function(){
            var name = $("#viewModal h5").text();
            var code = ace.edit("view_script").getValue();
            hook.save(code, name, true);
        });
    }
    this.finish_load_preset_table = function(){
        hook.content_search_form();
        hook.set_click();
        hook.setted_click();
        hook.delete_click();
        hook.view_click();
    }
    this.save = function(code, name, overwrite){
        $.ajax({
            url:"/save",
            type:"POST",
            data: JSON.stringify({"code": code, "name": name, "overwrite":overwrite}),
            success:function(res){
                if(res.result == "success"){
                    $("#saveModal").modal('hide');
                }else{
                    $("#saveModal p").addClass("text-danger");
                    $("#saveModal p").text(res.msg);
                }
            }
        });
    }
    this.modal_save = function(editor){
        $("#modal_save_button").off().on("click",function(){
            var code = editor.getValue();
            hook.save(code, $("#saveModal input").val(), false);
        });
    }
    this.scripts = function(){
        hook.modal_save(hook.code_editor);
        $("#save_button").off().on("click",function(){
            $("#saveModal").modal();

        });
        $("#preset_button").off().on("click", function(){
            $.ajax({
                url:"/saved",
                type:"GET",
                success: function(res){
                    $("#presetModal tbody").html(res);
                    hook.finish_load_preset_table();
                    $("#presetModal").modal();
                }
            });
        });
    }
}