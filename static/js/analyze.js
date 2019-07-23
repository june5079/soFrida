var analyze = new function(){
    this.spinner_div = "";
    this.source = "";
    this.credentials = "";
    this.init = function(){
        analyze.service = new Set();
        analyze.bucket = "";
        analyze.region = "";
        analyze.accesskeyid = "";
        analyze.secretkeyid = "";
        analyze.sessiontoken = "";
    }
    this.get_keys = function(){
        return {"service":Array.from(analyze.service),
                "bucket":analyze.bucket,
                "region":analyze.region,
                "accesskeyid":analyze.accesskeyid,
                "secretkeyid":analyze.secretkeyid,
                "sessiontoken":analyze.sessiontoken};
    }
    this.soFrida_start = function(socket){
        analyze.init();
        socket.emit("soFrida_start", {});
        socket.on("analyze_status", function(log){
            console.log(log);
            analyze.setData(log);
        });
    }
    this.setData = function(log){
        if(log.step == "frida_connect"){
            if(log.result == "success"){
                analyze.begreen("frida-connect", "frida-server connected with USB!");
            }else{
                $("#frida-connect-text").text("frida connect error : "+log.msg);
                
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
                if(analyze.spinner_div != "") analyze.spinner_div.remove();
                $("#apk-install-icon").show();
            }else if(log.result == "installing"){
                analyze.spinner("apk-install", "file installing start...");
            }else if(log.result == "not installed"){
                $("#apk-install-text").text(log.package+" is not installed...");
            }else{
                $("#apk-install-text").text("apk install error : "+log.msg);
            }
        }else if(log.step == "spawn"){
            if(log.result == "success"){
                analyze.begreen("spawn", "application is spawned !!");
            }else{
                $("#spawn-text").text("spawn error : "+log.msg);
            }
        }else if(log.step == "httprequest"){
            var class_name = log.class.substring(log.class.lastIndexOf(".")+1);
            analyze.begreen("httprequest", "class \""+class_name+"\" class is Loaded");
        }else if(log.step == "credentials"){
            var class_name = log.class.substring(log.class.lastIndexOf(".")+1);
            if(analyze.credentials == ""){
                analyze.credentials = class_name;
                analyze.begreen("credentials", "class \""+class_name+"\" class is Loaded. Tracing is Started!!");
            }else if(analyze.credentials != class_name){
                analyze.begreen("credentials", "class \""+analyze.credentials+", "+class_name+"\" class is Loaded. Tracing is Started!!");
            }
        }else if(log.step == "service"){
            analyze.service.add(log.name);
            analyze.begreen("service", "\""+Array.from(analyze.service).join(",")+"\" is used!!");
            if(log.name != "s3"){
                analyze.bucket = "nobucket";
                analyze.begreen("bucket", "This is not S3 Service!!");
            }
        }else if(log.step == "bucket"){
            analyze.begreen("bucket", "Bucket Name is \""+log.name+"\"!!");
            analyze.bucket = log.name;
        }else if(log.step == "region"){
            analyze.begreen("region", "Region is \""+log.name+"\"!!");
            analyze.region = log.name;
        }else if(log.step == "accesskeyid"){
            analyze.begreen("accesskeyid", "AccessKeyId is "+log.name);
            analyze.accesskeyid = log.name;
        }else if(log.step == "secretkeyid"){
            analyze.begreen("secretkeyid", "SecretKeyId is "+log.name);
            analyze.secretkeyid = log.name;
        }else if(log.step == "sessiontoken"){
            analyze.begreen("sessiontoken", "SessionToken is "+log.name);
            analyze.sessiontoken = log.name;
        }
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
}
