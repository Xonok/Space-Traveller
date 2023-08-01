const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}
var sock = new WebSocket("wss://"+location.host+"/chat_async")
sock.onopen = e=>{
	console.log(e)
	sock.send("hello")
}
sock.onmessage = e=>{
	console.log(e)
}