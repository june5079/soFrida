$.expr[":"].contains = $.expr.createPseudo(function(arg) {
    return function( elem ) {
        return $(elem).find("div").text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

function hexdump(buffer) {
    var blockSize = 16;
    var lines = [];
    var hex = "0123456789ABCDEF";
    for (var b = 0; b < buffer.length; b += blockSize) {
        var block = buffer.slice(b, Math.min(b + blockSize, buffer.length));
        var addr = ("0000" + b.toString(16)).slice(-4);
        var codes = block.map(function (ch) {
            var code = ch;
            return " " + hex[(0xF0 & code) >> 4] + hex[0x0F & code];
        }).join("");
        codes += "   ".repeat(blockSize - block.length);
        var chars = block.map(b => String.fromCharCode(b)).join("").replace(/[^ -~]+/g, '.');
        chars +=  " ".repeat(blockSize - block.length);
        lines.push(addr + " " + codes + "  " + chars);
    }
    return lines.join("<br>");
}
function pagination_search_form(class_list, card_name, class_table){
    /*$("#"+card_name+" #search_form").off().on("keyup", function(e){
        if(e.keyCode == 13){
            var curVal = $(this).val().toUpperCase();
            var filterd = class_list.filter(function(e){ return e.toUpperCase().indexOf(curVal) >= 0; });
            pagination.init(filterd, class_table);
            pagination.set(1);
            pagination_search_form(class_list, card_name, class_table);
        }
    });*/
    $("#"+card_name+" #search_form").off().on("propertychange change keyup paste input", function(){
        var curVal = $(this).val().toUpperCase();
        var filterd = class_list.filter(function(e){ return e.toUpperCase().indexOf(curVal) >= 0; });
        pagination.init(filterd, class_table);
        pagination.set(1);
        pagination_search_form(class_list, card_name, class_table);
    });
    $('#'+card_name+' .custom-control-input-item').off().on('change', function(){
        button_change(card_name);
        checkbox_change(card_name);
    });
    check_all(card_name);
}
function filter_search_form(card_name){
    $("#"+card_name+" #search_form").off().on("propertychange change keyup paste input", function(){
        var curVal = $(this).val().toUpperCase();
        $("#"+card_name+" tbody tr:contains('"+curVal+"')").show();
        $("#"+card_name+" tbody tr:not(:contains('"+curVal+"'))").hide();
    });
}
function non_filter_search_form(card_name){
    $("#"+card_name+" #search_form").off().on("keyup", function(e){
        if(e.keyCode == 13){
            var curVal = $(this).val().toUpperCase();
            $("#"+card_name+" tbody tr:contains('"+curVal+"')").show();
            $("#"+card_name+" tbody tr:not(:contains('"+curVal+"'))").hide();
        }
    });
}
function check_all(card_name){
    $("thead input").off();
    $("#"+card_name+" thead input").off().on("change", function(){
        var checked = $(this).prop("checked");
        $(this).parents(".table")
            .first()
            .find("tr[style!=\"display: none;\"]")
            .find("input[type=checkbox]")
            .prop("checked", checked);
            button_change(card_name);
    });
}
function button_change(card_name){
    var all = $('#'+card_name+' .custom-control-input-item');
    $('#'+card_name+" nav button").prop('disabled',function(){
        return all.filter(function(){ return $(this).prop('checked'); }).length === 0;
    });
}
function checkbox_change(card_name){
    var all = $('#'+card_name+' .custom-control-input-item');
    if(all.length == 0){
        $('#'+card_name+" .custom-control-input").prop('checked', false);
    }else{
        $("#"+card_name+" thead input").prop('checked',function(){
            return all.length === all.filter(function(){ return $(this).prop('checked'); }).length;
        });
    }
}
function finish_load_table(card_name){
    filter_search_form(card_name);
    $('#'+card_name+' .custom-control-input').prop('checked',false);
    $('#'+card_name+' .custom-control-input-item').off().on('change', function(){
        button_change(card_name);
        checkbox_change(card_name);
    });
    check_all(card_name);
}
function htmlDecode(input)
{
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
}
function select_device(){
    $.ajax({
        url:"/devices",
        type:"GET",
        success:function(res){
            $("#devices tbody").html(res);
            $("#devicesModal").modal();
        }
    });
    /*let socket = io.connect("http://" + document.domain + ":" + location.port + "/device");
    socket.on("devices_res", function(data){
        devices_table_modal(data.devices, page);
    });
    socket.emit("devices", function(){});*/
}
function device_after_table(serial){
    //uri = "/"+"installed_list"+"/" or "/"+"ios_process_list"+"/"
    var uri = document.baseURI.substring(document.baseURI.lastIndexOf('/')+1);
    uri = uri.replace("#","");
    if(!uri.startsWith("installed") && !uri.startsWith("ios_process")){
        set_serial(serial);
        if(document.baseURI.indexOf("/dex/")){
            get_process();
        }else{
            location.reload(true);
        }
    }else{
        $.ajax({
            url:"/"+uri+"_list/"+serial,
            type:"GET",
            success:function(res){
                $("#"+uri+"_card tbody").html(res);
                $("#devicesModal").modal('hide');

                $("#current_device").text(serial);
                $("#current_device").prop('hidden', false);
                
                finish_load_table(uri+"_card");
            }
        });
    }
}
function set_serial(serial){
    $.ajax({
        url:"/serial/"+serial,
        type:"GET",
        success:function(res){
            $("#devicesModal").modal('hide');

            $("#current_device").text(res.serial);
            $("#current_device").prop('hidden', false);
        }
    });
}
function device_connect(mode){
    var socket_device = io.connect("http://" + document.domain + ":" + location.port + "/device");
    socket_device.on("device", function(data){
        var devices = data.devices;
        if(devices.length == 0){
            alert("error: no devices/emulators found");
        }else if(devices.length == 1){
            if(mode.startsWith("installed")){
                device_after_table(devices[0].serial);
            }else if(mode.startsWith("ios_process")){
                device_after_table(devices[0].serial);
            }else{
                set_serial(devices[0].serial);
            }
        }else{
            select_device();
        }
        socket_device.close();
    });
}
function current_serial(){
    $.ajax({
        url:"/device",
        type:"GET",
        success:function(res){
            if(res.serial != ""){
                $("#current_device").text(res.serial);
                $("#current_device").prop('hidden', false);
            }
        }
    });
}
/*function devices_table_modal(devices, page){
    $("#devices tbody").html("");
    for(var i=0;i<devices.length;i++){
        var td = "<td>"+devices[i].serial+"</td>"+"<td>"+devices[i].status+"</td>";
        td += "<td><a class=\"btn btn-danger\" href=\"/"+page+"/serial/"+devices[i].serial+"\">Select</a></td>";
        var tr = "<tr>"+td+"</tr>";
        $("#devices tbody").append(tr);
    }
    $("#devicesModal").modal();
}*/
function select_pid(pid){
    $.ajax({
        url:"/process/"+pid,
        type:"GET",
        success:function(res){
            $("#class_card tbody").html(res);
            $("#processModal").modal("hide");
        }
    });
}
function select_process(processes){
    $("#processes tbody").html();
    for(var i=0;i<processes.length;i++){
        var td = "<td>"+processes[i].pid+"</td>"+"<td>"+processes[i].name+"</td>";
        td += "<td><button class=\"btn btn-danger\" onclick=select_pid("+processes[i].pid+")>Select</button></td>";
        var tr = "<tr>"+td+"</tr>";
        $("#processes tbody").append(tr);
    }
    $("#processModal").modal();
}
function get_process(){
    var socket_process = io.connect("http://" + document.domain + ":" + location.port + "/process");
    socket_process.on("process", function(data){
        if(data.processes.length == 0){
            //alert("Check ADB Connect and Frida Server Connect!!")
            select_device();
        }else{
            var process = "";
            for(var i =0;i<data.processes.length;i++){
                if(i == 0){
                    process += "<button type='button' class='btn btn-secondary mr-1'>"+ data.processes[i].name+"("+data.processes[i].pid+")</button>";
                }else{
                    process += "<button type='button' class='btn btn-outline-secondary mr-1'>"+ data.processes[i].name+"("+data.processes[i].pid+")</button>";
                }
            }
            $("#process_list").html(process);
            $("#process_list button").on("click", function(e){
                var selected = $(this).text();
                var buttons = $("#process_list button");
                for(var i=0;i<buttons.length;i++){
                    var button = $(buttons[i]);
                    if(button.text() == selected){
                        button.removeClass();
                        button.addClass("btn btn-secondary mr-1");
                    }else{
                        button.removeClass();
                        button.addClass("btn btn-outline-secondary mr-1");
                    }
                }
            });
            //hook.init();
        }
        //socket_process.close();
    });
    return socket_process;
}
function finish_load_code(code_card){
    $("#"+code_card+" code").on("paste", function(e){
        e.preventDefault();
        var pastedData = e.originalEvent.clipboardData.getData('text');
        e.target.ownerDocument.execCommand("insertText", false, pastedData);
        let savedSel = rangy.saveSelection();
        hljs.highlightBlock(code_snif);
        rangy.restoreSelection(savedSel);
    });
    var code_snif = $("#"+code_card+" code")[0];
    hljs.highlightBlock(code_snif);
    $("#"+code_card+" code").on('keydown', function(e){
        if(e.keyCode == 9){
            document.execCommand('insertHTML', false, '&#009');
            if(e.preventDefault){
                e.preventDefault();
            }
        }
    });
    $("#"+code_card+" code").on('keyup', function(e){
        if(e.keyCode == 13 || e.keyCode == 32){
            let savedSel = rangy.saveSelection();
            hljs.highlightBlock(code_snif);
            rangy.restoreSelection(savedSel);
        }
    });    
}