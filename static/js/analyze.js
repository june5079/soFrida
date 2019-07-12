var analyze = new function(){
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
    this.log_start = function(){
        var source = new EventSource('/analyze_status');
		source.onmessage = function (event) {
            var log = JSON.parse(event.data);
            if(log.step == "frida_connect"){
                if(log.result == "success"){
                    analyze.begreen("frida-connect", "frida-server connected with USB!");
                }else{
                    $("#frida-connect-text").text("frida connect error : "+log.msg)
                }
            }else if(log.step == "adb_connect"){
                if(log.result == "success"){
                    analyze.begreen("adb-connect", "adb connected with USB!");
                }else{
                    $("#adb-connect-text").text("adb connect error : "+log.msg);
                }
            }else if(log.step == "apk_install"){
                if(log.result == "installed"){
                    analyze.begreen("apk-install", log.package+" is installed!!");
                    this.close();
                }else if(log.result == "installing"){
                    $("#apk-install-text").text(log.package+" file installing start...");
                }else if(log.result == "not installed"){
                    $("#apk-install-text").text(log.package+" is not installed...");
                }else{
                    $("#apk-install-text").text("apk install error : "+log.msg);
                }
            }
            else if(log.step == "waiting"){
                
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
