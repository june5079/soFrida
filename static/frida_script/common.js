function get_classes(){
    Java.perform(function(){
        send(Java.enumerateLoadedClassesSync());
    });
    send("complete");
}
