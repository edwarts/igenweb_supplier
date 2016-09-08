// function nTabs2(thisObj,Num){
//     if(thisObj.className == "active")return;
//     var tabObj = thisObj.parentNode.id;
//     var tabList = document.getElementById(tabObj).getElementsByTagName("li");
//     for(var i=0; i <tabList.length; i++) {
//         if (i == Num) {
//             thisObj.className = "a";
//             document.getElementById(tabObj+"_Content"+i).style.display = "block";
//         } else {
//             tabList[i].className = "n";
//             document.getElementById(tabObj+"_Content"+i).style.display = "none";
//         }
//     }
//     event.preventDefault();
// }
// by wanggp
// ******** 根据标签类型筛选碎片
function nTabs1(thisObj,Num){
    if(thisObj.className == "a")return;
    if(!$("#cpcjxcbotzy_"+Num).html()){
        var cityid = $("[name='city']")[0].id;
        $.ajax({
            url:'/auth/getcitypiece/'+cityid+'/'+Num,
            datatype:"json",
            //data:{id:cityid, type:Num},
            success:function(data) {
                var data = eval(data);
                $("#cpcjxcbotzy_"+Num).find(".chuangjlxc5d").remove();
                for(var i=0;i<data.length;i++) {
                    //var title = data[i].description.substr(0, 15);
                    suipian_html = "                    <div class='chuangjlxc5d'>\
                            <div class='chuangjlxc5d1'><img src='http://p.igenwo.com/static/"+data[i].cover+"'></div>\
                            <div class='chuangjlxc5d2'>\
                                <input type='hidden' name='pieceid' value='"+data[i].id+"' />\
                                <h3>"+data[i].name_cn+"</h3>\
                                <h4>"+data[i].description+"</h4>\
                                <h5><span>时长：1.5大小时</span><em><i>"+data[i].price+"</i>元起</em></h5>\
                            </div>\
                            <div class='chuangjlxc5d3'><a href='#'>+ 添加到行程</a></div>\
                        </div>";
                    $(suipian_html).appendTo($("#cpcjxcbotzy_"+Num));
                }
                document.getElementById("getmore_count").value = 1;
            }
        });
    }
    
    var li=$("div.chuangjlxc4z_xc li").index(thisObj);
    $("div#myTab0_Content1>div#cpcjxcbotzy_my").hide();
    $("div#myTab0_Content1>div.tab_list").hide();
    $("div#myTab0_Content1>div.tab_list:eq("+li+")").show();
    $("div#myTab0_Content1>div.jiazaimore").show();
    // var tabObj = thisObj.parentNode.id;
    // var tabList = document.getElementById(tabObj).getElementsByTagName("li");
    // len = tabList.length;
    // for(i=1; i <len; i++) {
    //     if (i == Num) {
    //         thisObj.className = "a";
    //         document.getElementById("cpcjxcbotzy_"+i).style.display = "block";
    //     } else {
    //         tabList[i].className = "n";
    //         document.getElementById("cpcjxcbotzy_"+i).style.display = "none";
    //     }
    // }
    event.preventDefault();
}
// ********