!function(){
    function start_download(){

    };
    function google_login(){
        $("#loginModal").prop("aria-hidden", false);
    };
}
var download = new function(){
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
    this.log_start = function(){
        var source = new EventSource('/download_log');
		source.onmessage = function (event) {
            var log = JSON.parse(event);
            /*
            log = {"step":"start", "pkg_name":"com.happylabs.hps"};
            log = {"step":"finish", "pkg_name":"com.happylabs.hps"};
            log = {"step":"error", "msg":"request_error", "pkg_name":"com.happylabs.hps"};
            */
        }
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
