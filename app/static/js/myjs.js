/**
 * Created by king on 2016/3/7.
 */
function html_decode(str) {
    var s = "";
    if (str.length == 0) return "";
    s = str.replace(/&gt;/g, "&");
    s = s.replace(/&lt;/g, "<");
    s = s.replace(/&gt;/g, ">");
    s = s.replace(/&nbsp;/g, " ");
    s = s.replace(/&#39;/g, "\'");
    s = s.replace(/&quot;/g, "\"");
    s = s.replace(/&#34;/g, "\"");
    s = s.replace(/<br>/g, "\n");
    return s;
}

// 建立一个可存取到该file的url
function getObjectURL(file) {
	var url = null ;
	if (window.createObjectURL!=undefined) { // basic
		url = window.createObjectURL(file) ;
	} else if (window.URL!=undefined) { // mozilla(firefox)
		url = window.URL.createObjectURL(file) ;
	} else if (window.webkitURL!=undefined) { // webkit or chrome
		url = window.webkitURL.createObjectURL(file) ;
	}
	return url ;
}

function upladFiles(path) {
    var fileObj = document.getElementById("suipianimg").files; // 获取文件对象
    var FileController = path;                    // 接收上传文件的后台地址
    // FormData 对象
    var form = new FormData();
    for(var i=0; i<fileObj.length; i++) {
        form.append("file"+i, fileObj[i]);                           // 文件对象
    }
    //form.append("file", fileObj);
    // XMLHttpRequest 对象
    var xhr = new XMLHttpRequest();
    xhr.open("post", FileController, false);
    xhr.onload = function () {
    };
    xhr.send(form);
    if (xhr.status == 200){
        var x = xhr.responseText;
        if (x != "")
            alert(xhr.responseText);
    }
}

// 正则验证email Edgar 2016.6.15
function isEmail(str){
       var reg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/;
       return reg.test(str);
}

// 页首退出登录按钮
$("a#loginout_btn").click(function(event) {
    alert("ok");
    window.location.href='/auth/loginout';
});

// 处理存储的大容量HTML文本函数
function _TEXT(wrap) {  
    return wrap.toString().match(/\/\*\s([\s\S]*)\s\*\//)[1];  
} 

// 日期加一天 Edgar 2016.6.21
function date_add1(date_now){
    var mm=date_now; 
    var arr = mm.split("-");  
    var newdt = new Date(Number(arr[0]),Number(arr[1])-1,Number(arr[2])+1);  
    repnewdt = newdt.getFullYear() + "-" +   (newdt.getMonth()+1) + "-" + newdt.getDate();  
    return repnewdt;
}

// 删除最后一个字符
function del_last_word(text){
    newtext=text.substring(0,text.length-1);
    return newtext;
}

//-----------------------------
//乘法函数，用来得到精确的乘法结果 
//说明：javascript的乘法结果会有误差，在两个浮点数相乘的时候会比较明显。这个函数返回较为精确的乘法结果。 
//调用：accMul(arg1,arg2) 
//返回值：arg1乘以arg2的精确结果 
function accMul(arg1,arg2) 
{ 
var m=0,s1=arg1.toString(),s2=arg2.toString(); 
try{m+=s1.split(".")[1].length}catch(e){} 
try{m+=s2.split(".")[1].length}catch(e){} 
return Number(s1.replace(".",""))*Number(s2.replace(".",""))/Math.pow(10,m) 
} 
//给Number类型增加一个mul方法，调用起来更加方便。 
Number.prototype.mul = function (arg){ 
return accMul(arg, this); 
} 
//-------------------
//除法函数，用来得到精确的除法结果 
//说明：javascript的除法结果会有误差，在两个浮点数相除的时候会比较明显。这个函数返回较为精确的除法结果。 
//调用：accDiv(arg1,arg2) 
//返回值：arg1除以arg2的精确结果 

function accDiv(arg1,arg2){ 
var t1=0,t2=0,r1,r2; 
try{t1=arg1.toString().split(".")[1].length}catch(e){} 
try{t2=arg2.toString().split(".")[1].length}catch(e){} 
with(Math){ 
r1=Number(arg1.toString().replace(".","")) 
r2=Number(arg2.toString().replace(".","")) 
return (r1/r2)*pow(10,t2-t1); 
} 
} 
//----------------------
//加法函数，用来得到精确的加法结果 
//说明：javascript的加法结果会有误差，在两个浮点数相加的时候会比较明显。这个函数返回较为精确的加法结果。 
//调用：accAdd(arg1,arg2) 
//返回值：arg1加上arg2的精确结果 
function accAdd(arg1,arg2){ 
var r1,r2,m; 
try{r1=arg1.toString().split(".")[1].length}catch(e){r1=0} 
try{r2=arg2.toString().split(".")[1].length}catch(e){r2=0} 
m=Math.pow(10,Math.max(r1,r2)) 
return (arg1*m+arg2*m)/m 
} 
//给Number类型增加一个add方法，调用起来更加方便。 
Number.prototype.add = function (arg){ 
return accAdd(arg,this); 
} 
// ---------
//减法函数，用来得到精确的减法结果 
//说明：javascript的减法结果会有误差，在两个浮点数相加的时候会比较明显。这个函数返回较为精确的减法结果。 
//调用：accSubtr(arg1,arg2) 
//返回值：arg1减去arg2的精确结果 
function accSubtr(arg1,arg2){
var r1,r2,m,n;
try{r1=arg1.toString().split(".")[1].length}catch(e){r1=0}
try{r2=arg2.toString().split(".")[1].length}catch(e){r2=0}
m=Math.pow(10,Math.max(r1,r2));
//动态控制精度长度
n=(r1>=r2)?r1:r2;
return ((arg1*m-arg2*m)/m).toFixed(n);
} 
//给Number类型增加一个subtr 方法，调用起来更加方便。 
Number.prototype.subtr = function (arg){ 
return accSubtr(arg,this); 
} 

// 格式化价格 保留两位小数
function c2dot(price){
    if(price.toString().indexOf(".")==-1){
        price=price.toString()+".00";
    }else{
        price=price.toString();
        // 小数位数只有1位的情况,就在末尾加上个0
        if(price.length-1-price.indexOf(".")==1){
            price=price+"0";
        }
    }
    price=parseFloat(price);
    price=price.toFixed(2);
    return price.toString();
}