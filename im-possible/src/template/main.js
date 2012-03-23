var request = false;
try {
  request = new XMLHttpRequest();
} catch (trymicrosoft) {
  try {
    request = new ActiveXObject("Msxml2.XMLHTTP");
  } catch (othermicrosoft) {
    try {
      request = new ActiveXObject("Microsoft.XMLHTTP");
    } catch (failed) {
      request = false;
    }
  }
}

if (!request)
  alert("Error initializing XMLHttpRequest!");
  
function ajaxSendRequest(url) {
	if (request.readyState==0 || request.readyState==4) {
		request.open("GET", url, true);
		request.onreadystatechange = ajaxUpdatePage;
		request.send(null);
	}	
}

function ajaxUpdatePage() {
	if (request.readyState==4 && request.status==200) {
		try {
			responseValue=request.responseText;
			if (responseValue) {
				eval(responseValue);
			}
		} catch (e) {
			alert("Error processing ajax response "+e);
		}
	} 
} 


///////////////////////////////////////////////////////
// Response handler for post voting
function doneVote(postKey,voteCount) {
	var voteDiv=document.getElementById("vote_"+postKey);
	voteDiv.innerHTML=voteCount;
	document.getElementById("vote_link_"+postKey).style.display="none";
	document.getElementById("voted_"+postKey).style.display="";
}

////////////////////////////////////////////////////////////
// Response handler for administrator ajax request for banning user
function doneBanUser(userEmail) {
	alert("User banned "+userEmail)
}



//////////////////////////////////////////////////////////////////
function getAbsoluteDivs()  
{  
    var arr = new Array();  
    var all_divs = document.body.getElementsByTagName("DIV");  
    var j = 0;  
  
    for (i = 0; i < all_divs.length; i++)  
        if (all_divs.item(i).style.position=='absolute')  
        {  
            arr[j] = all_divs.item(i);  
            j++;  
        }  
  
    return arr;  
}  
  
function bringToFront(id)  
{  
    if (!document.getElementById ||  
        !document.getElementsByTagName)  
        return;  
  
    var obj = document.getElementById(id);  
    var divs = getAbsoluteDivs();  
    var max_index = 0;  
    var cur_index;  
  
    // Compute the maximal z-index of  
    // other absolute-positioned divs  
    for (i = 0; i < divs.length; i++)  
    {  
        var item = divs[i];  
        if (item == obj ||  
            item.style.zIndex == '')  
            continue;  
  
        cur_index = parseInt(item.style.zIndex);  
        if (max_index < cur_index)  
        {  
            max_index = cur_index;  
        }  
    }  
  
    obj.style.zIndex = max_index + 1;  
}  
  
function sendToBack(id)  
{  
    if (!document.getElementById ||  
        !document.getElementsByTagName)  
        return;  
  
    var obj = document.getElementById(id);  
    var divs = getAbsoluteDivs();  
    var min_index = 999999;  
    var cur_index;  
  
    if (divs.length < 2)  
        return;  
  
    // Compute the minimal z-index of  
    // other absolute-positioned divs  
    for (i = 0; i < divs.length; i++)  
    {  
        var item = divs[i];  
        if (item == obj)  
            continue;  
  
        if (item.style.zIndex == '')  
        {  
            min_index = 0;  
            break;  
        }  
  
        cur_index = parseInt(item.style.zIndex);  
        if (min_index > cur_index)  
        {  
            min_index = cur_index;  
        }  
  
    }  
  
    if (min_index > parseInt(obj.style.zIndex))  
    {  
        return;  
    }  
  
    obj.style.zIndex = 1;  
  
    if (min_index > 1)  
        return;  
  
    var add = min_index == 0 ? 2 : 1;  
  
    for (i = 0; i < divs.length; i++)  
    {  
        var item = divs[i];  
        if (item == obj)  
            continue;  
  
        item.style.zIndex += add;  
    }  
}  

//////////////////////////////////////////////////////
//Determining window size
function f_clientWidth() {
	return f_filterResults (
		window.innerWidth ? window.innerWidth : 0,
		document.documentElement ? document.documentElement.clientWidth : 0,
		document.body ? document.body.clientWidth : 0
	);
}
function f_clientHeight() {
	return f_filterResults (
		window.innerHeight ? window.innerHeight : 0,
		document.documentElement ? document.documentElement.clientHeight : 0,
		document.body ? document.body.clientHeight : 0
	);
}
function f_scrollLeft() {
	return f_filterResults (
		window.pageXOffset ? window.pageXOffset : 0,
		document.documentElement ? document.documentElement.scrollLeft : 0,
		document.body ? document.body.scrollLeft : 0
	);
}
function f_scrollTop() {
	return f_filterResults (
		window.pageYOffset ? window.pageYOffset : 0,
		document.documentElement ? document.documentElement.scrollTop : 0,
		document.body ? document.body.scrollTop : 0
	);
}
function f_filterResults(n_win, n_docel, n_body) {
	var n_result = n_win ? n_win : 0;
	if (n_docel && (!n_result || (n_result > n_docel)))
		n_result = n_docel;
	return n_body && (!n_result || (n_result > n_body)) ? n_body : n_result;
}



//////////////////////////////////////////////////////
// Javascript dialog
function JSDialog(divHeader, divContent, preferredWidth, preferredHeight) {
	this.divHeader=divHeader;
	this.divContent=divContent;
	this.preferredWidth=preferredWidth;
	this.preferredHeight=preferredHeight;	
	
  this.divHeader.style.display="none";	
	this.divContent.style.display="none";
}

JSDialog.prototype.show = function() {
	dialogTop=document.body.scrollTop+(f_clientHeight()-this.preferredHeight)/2;
	headerHeight=24;
	
  this.divHeader.style.position="absolute";
  this.divHeader.style.top=dialogTop;
  this.divHeader.style.left=f_scrollLeft()+(f_clientWidth()-this.preferredWidth)/2;
  this.divHeader.style.width=this.preferredWidth;
  this.divHeader.style.height=headerHeight;
  //this.divHeader.style.zIndex=0;
  
  //alert(this.divHeader.style.top+" "+this.divHeader.style.height);
  
  this.divContent.style.position="absolute";
  this.divContent.style.top=dialogTop+headerHeight;
  this.divContent.style.left=f_scrollLeft()+(f_clientWidth()-this.preferredWidth)/2;
  this.divContent.style.width=this.preferredWidth;
  this.divContent.style.height=this.preferredHeight-headerHeight;
  //this.divContent.style.zIndex=0;
  	
  this.divHeader.style.display="";
  this.divContent.style.display="";
  
  bringToFront(this.divHeader.id);
  bringToFront(this.divContent.id);
}

JSDialog.prototype.hide = function() {
	this.divHeader.style.display="none";
	this.divContent.style.display="none";
}


/////////////////////////////////////////////////////////
//String functions 
function isInvisibleChar(c) {
    return c==" " || c=="\n" || c=="\r" || c=="\t";
}

function String_trim() {
    var start=0;
    var finish=this.length;
    var i=0;

    while (i<this.length && isInvisibleChar(this.charAt(i))) {
        start++;
        i++;
    }

    if (i>=this.length) {
        return "";
    }

    i=this.length-1;
    while (i>=0 && isInvisibleChar(this.charAt(i))) {
        finish--;
        i--;
    }

    return this.substring(start,finish);
}

String.prototype.trim=String_trim;
