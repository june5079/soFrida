var pagination = new function(){
    
    this.init = function(list, callback){
        this.list = list;
        this.callback = callback;
        this.last_num =  Math.floor(pagination.list.length / 10);
        if(pagination.list.length % 10 > 0){
            this.last_num += 1;
        }
    }
    this.set = function(index){
        var start = (index-1)*10;
        var end = (index-1)*10+10;
        if(pagination.list.length < end){
            end = pagination.list.length;
        }
        pagination.callback(pagination.list.slice(start, end));
        pagination.pagebar(index);
    }
    this.mark = {
        "first":"&laquo;",
        "last":"&raquo;",
        "prev":"&lt;",
        "next":"&gt;"
    }
    this.jump = function(dir, index){
        return "<li class='page-item'><a class='page-link' href='#' onclick=pagination.set("+index+") aria-label='Previous'>"+
        "<span aria-hidden='true'>"+pagination.mark[dir]+"</span><span class='sr-only'>Previous</span></a></li>";
    }
    this.item = function(i, index){
        var active = "";
        var primary = ""
        if(i == index){
            active = " active";
        }
        return "<li class='page-item"+active+"'><a class='page-link' onclick=pagination.set("+i+") href='#'>"+i+"</a></li>";
    }
    this.pagebar = function(index){
        var index_start = 0;
        if(index % 10 == 0){
            index_start = index - 9;
        }else{
            index_start = Math.floor(index/10) * 10 + 1;
        }
        var index_end = index_start + 9;
        if(index_end > pagination.last_num){
            index_end = pagination.last_num;
        }
        var index_list = "";

        if(index_start != 1){
            index_list += pagination.jump("first", 1);
            var prev = index_start - 1;
            if(prev < 1){
                prev = 1;
            }
            index_list += pagination.jump("prev", prev);
        }
        
        for(var i = index_start;i<=index_end;i++){
            index_list += pagination.item(i, index);
        }
        
        if(index_end != pagination.last_num){
            var next = index_start + 10; 
            if(next > pagination.last_num){
                next = pagination.last_num;
            }
            index_list += pagination.jump("next", next);
            index_list += pagination.jump("last", pagination.last_num);
        }
        $(".pagination").html(index_list);
    }
}