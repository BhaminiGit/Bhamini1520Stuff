var time = 1000;
var timeId;

function setup(){

	document.getElementById("postButton").addeventListener("click", postMessage,true);

}

function postMessage(){
	var httpRequest = new XMLHttpRequest();

	if(!httpRequest)
	{
		return false;
	}

	var theMsg = document.getElementById("message").value;
	httpRequest.onreadystatechange = function() {handlingMessage(httpRequest,theMsg)};

	httpRequest.open("POST", "/currentRoom");
	httpRequest.setRequestHeader("Content-Type",'application/x-www-form-urlencoded')

	var data = "message=" + theMsg;

	httpRequest.send(data);

}

function handlingMessage(httpRequest,theMsg)
{
	if(httpRequest.readyState === XMLHttpRequest.DONE){
		if(httpRequest.status === 200){
			addMsg(theMsg);
		}
	}
}

function poller(){

	var httpRequest = new XMLHttpRquest
	if(!httpRequest){
		return false;
	}

	httpRequest.onreadystatechange = function(){handlingMessage(httpRequest)};
	httpRequest.open('get')
}

function addMsg(msg){

	var bubble = document.createElement('P');
	bubble.innerHTML = msg;
	bubble.classList.add('messageBubbles');
	document.getElementById("messageHistory").appendChild(bubble);

	document.getElementById("message").value = "";

}