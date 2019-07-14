var analyze = new function(){
    this.spinner_div = "";
    this.source = "";
    this.credentials = "";
    this.init = function(){
        analyze.service = ""
        analyze.bucket = ""
        analyze.region = ""
        analyze.accesskeyid = ""
        analyze.secretkeyid = ""
        analyze.sessiontoken = ""
    }
    this.soFrida_start = function(){
        $.ajax({
            url:"/soFrida_start",
            type:"GET",
            success:function(res){
                if(res.result == "success"){
                    analyze.init();
                    analyze.log_start();
                }
            }
        })
    }
    this.begreen = function(step, text){
        $("#"+step+"-icon").attr("style","color:green");
        var ml = $("#"+step+"-icon").hasClass("ml-3");
        $("#"+step+"-icon").removeClass();
        if(ml){
            $("#"+step+"-icon").addClass("fas fa-fw fa-check ml-3");       
        }else{
            $("#"+step+"-icon").addClass("fas fa-fw fa-check"); 
        }
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
    this.check = function(){
        if(analyze.service == "") return false;
        if(analyze.bucket == "") return false;
        if(analyze.region == "") return false;
        if(analyze.accesskeyid == "") return false;
        if(analyze.secretkeyid == "") return false;
        if(analyze.accesskeyid == "") return false;
        return true;
    }
    this.stop_log = function(){
        console.log("stop");
        if(analyze.source != ""){ 
            analyze.source.close();
            analyze.source = "";
        }
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
                    analyze.begreen("spawn", "application is spawned !!");
                    analyze.next_step("spawn")
                }else{
                    $("#spawn-text").text("spawn error : "+log.msg);
                }
            }else if(log.step == "httprequest"){
                var class_name = log.class.substring(log.class.lastIndexOf(".")+1);
                analyze.begreen("httprequest", "class \""+class_name+"\" class is Loaded");
                analyze.next_step("httprequest");
            }else if(log.step == "credentials"){
                var class_name = log.class.substring(log.class.lastIndexOf(".")+1);
                if(analyze.credentials == ""){
                    analyze.credentials = class_name;
                    analyze.begreen("credentials", "class \""+class_name+"\" class is Loaded. Tracing is Started!!");
                }else if(analyze.credentials != class_name){
                    analyze.begreen("credentials", "class \""+analyze.credentials+", "+class_name+"\" class is Loaded. Tracing is Started!!");
                }
                analyze.next_step("credentials");
            }else if(log.step == "service"){
                analyze.begreen("service", "\""+log.name+"\" is used!!");
                analyze.service = log.name;
                if(log.name != "s3"){
                    analyze.bucket = "nobucket";
                    analyze.begreen("bucket", "This is not S3 Service!!");
                }
                analyze.next_step("service");
            }else if(log.step == "bucket"){
                analyze.begreen("bucket", "Bucket Name is \""+log.name+"\"!!");
                analyze.bucket = log.name;
                analyze.next_step("bucket");
            }else if(log.step == "region"){
                analyze.begreen("region", "Region is \""+log.name+"\"!!");
                analyze.region = log.name;
                analyze.next_step("region");
            }else if(log.step == "accesskeyid"){
                analyze.begreen("accesskeyid", "AccessKeyId is "+log.name);
                analyze.accesskeyid = log.name;
                analyze.next_step("accesskeyid");
            }else if(log.step == "secretkeyid"){
                analyze.begreen("secretkeyid", "SecretKeyId is "+log.name);
                analyze.secretkeyid = log.name;
                analyze.next_step("secretkeyid");
            }else if(log.step == "sessiontoken"){
                analyze.begreen("sessiontoken", "SessionToken is "+log.name);
                analyze.sessiontoken = log.name;
                analyze.next_step("sessiontoken");
            }/*else if(log.step == "stop"){
                analyze.next_step("stop");
                this.close();
            }*/
            if(analyze.check()){
                this.close();
                analyze.next_step("guicomplete")
            }
        }
    }
}
