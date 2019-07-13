var analyze = new function(){
    this.spinner_div = "";
    this.source = "";
    this.soFrida_start = function(){
        $.ajax({
            url:"/soFrida_start",
            type:"GET",
            success:function(res){
                if(res.result == "success")
                    analyze.log_start();
            }
        })
    }
    this.begreen = function(step, text){
        $("#"+step+"-icon").attr("style","color:green");
        $("#"+step+"-icon").removeClass();
        $("#"+step+"-icon").addClass("fas fa-fw fa-check");   
        $("#"+step+"-text").text(text);
    }
    this.spinner = function(step, text){
        $("#"+step+"-text").text(text);
        if($("#apk-install-icon").next().hasClass("spinner-border spinner-border-sm")) return analyze.spinner_div;
        analyze.spinner_div = $("<div class=\"spinner-border spinner-border-sm\" role=\"status\"><span class=\"sr-only\">Loading...</span></div> ");
        $("#"+step+"-icon").hide();
        var div = $("#"+step+"-icon");
        analyze.spinner_div.insertAfter(div);
        return analyze.spinner_div;
    }
    this.next_step = function(step){
        $.ajax({
            url:"/next_step/"+step,
            type:"GET",
            success:function(res){
                
            }
        })
    }
    this.stop_log = function(){
        console.log("stop");
        analyze.source.close();
        analyze.source = "";
        analyze.next_step("stop")
    }
    this.log_start = function(){
        analyze.source = new EventSource('/analyze_status');
		analyze.source.onmessage = function (event) {
            var log = JSON.parse(event.data);
            if(log.step == "frida_connect"){
                if(log.result == "success"){
                    analyze.begreen("frida-connect", "frida-server connected with USB!");
                    analyze.next_step("frida-connect")
                }else{
                    $("#frida-connect-text").text("frida connect error : "+log.msg);
                    
                }
            }else if(log.step == "adb_connect"){
                if(log.result == "success"){
                    analyze.begreen("adb-connect", "adb connected with USB!");
                    analyze.next_step("adb-connect")
                }else{
                    $("#adb-connect-text").text("adb connect error : "+log.msg);
                }
            }else if(log.step == "apk_install"){
                if(log.result == "installed"){
                    analyze.begreen("apk-install", log.package+" is installed!!");
                    analyze.next_step("apk-install")
                    if(analyze.spinner_div != "") analyze.spinner_div.remove();
                    $("#apk-install-icon").show();
                }else if(log.result == "installing"){
                    analyze.spinner("apk-install", "file installing start...");
                    analyze.next_step("apk-installing");
                }else if(log.result == "not installed"){
                    $("#apk-install-text").text(log.package+" is not installed...");
                    analyze.next_step("apk-not-installed")
                }else{
                    $("#apk-install-text").text("apk install error : "+log.msg);
                }
            }else if(log.step == "spawn"){
                if(log.result == "success"){
                    analyze.begreen("spawn", "spawned application!!");
                    analyze.next_step("spawn")
                    this.close();
                }else{
                    $("#spawn-text").text("spawn error : "+log.msg);
                }
            }else if(log.step == "waiting"){
                
            }
            /*
            log = {"step":"frida_connect", "result":"success"};
            log = {"step":"finish", "pkg_name":"com.happylabs.hps"};
            log = {"step":"error", "msg":"request_error", "pkg_name":"com.happylabs.hps"};
            */
        }
    }
    this.download_start = function(){
        var package_list = [];
        $('.custom-control-input-item').filter(function(){
            return $(this).prop('checked');}).each(function(){
                package_list.push($(this).attr('id'));
            });

        $.ajax({
            url:'/download',
            type:'POST',
            contentType: "application/json; charset=utf-8",
            data:JSON.stringify({"list":package_list}),
            success:function(res){
                download.log_start();
            }
        });
    }
    
    this.open_google_login = function(){
        $("#loginModal").attr("aria-hidden", false);
        $("#loginModal").modal();
    }
    this.google_login = function(id, pw){
        $.ajax({
            url:'/google_login',
            type:'POST',
            data: {'id':id,'pw':pw},
            success:function(res){
                if(res.result == "success"){
                    $("#login_alert").html("<p class=\"text-success\">Login success!</p>");
                    $("#loginModal").attr("aria-hidden", true);
                    $("#loginModal").modal("hide");
                    $("#login_alert").attr("aria-hidden", true);
                    download.download_start();
                }else{
                    $("#inputPassword").val("");
                    $("#login_alert").html("<p class=\"text-danger\">Login fail!</p><p class=\"text-info\"><a href=\"https://accounts.google.com/b/0/DisplayUnlockCaptcha\">Unlock Google Account</p>");
                    $("#login_alert").attr("aria-hidden", false);
                }
            }
        });
    }
}
