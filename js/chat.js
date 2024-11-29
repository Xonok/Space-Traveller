/*
CODE STATUS - unfinished
This thing barely does anything.
*Need to write the rest of the protocol logic, including the option for long messages.
*There is no chat code as of yet.
*/

const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}
var sock = new WebSocket("wss://"+location.host+"/chat_async")
sock.onopen = e=>{
	console.log(e)
	sock.send(JSON.stringify({"msg":"hello"}))
}
sock.onmessage = e=>{
	console.log(e)
}