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

var chat_socket
var last_message_idx = -1

function chat_connect(){
	chat_socket = new WebSocket("wss://"+location.host+"/chat_async")
	
	chat_socket.onopen = e=>{
		console.log(e)
		// chat_socket.send(JSON.stringify({"msg":"hello"}))
		chat_command("get-messages",{"idx":last_message_idx})
	}
	chat_socket.onmessage = e=>{
		var msg = JSON.parse(e.data)
		var evt = msg.event
		var data = msg.data
		console.log(e,evt,data)
		if(!evt){
			console.log(e)
			return
		}
		if(evt === "msg-receive"){
			window.chat_log.innerHTML += msg.data.sender+msg.data.time+msg.data.txt+"<br>"
		}
		if(evt === "msg-receive-multi"){
			msg.data.forEach(d=>{
				window.chat_log.innerHTML += d.sender+d.time+d.txt+"<br>"
			})
		}
	}
	chat_socket.onerror = e=>{
		chat_socket.close()
	}
	chat_socket.onclose = e=>{
		setTimeout(chat_connect,1000)
	}
}
function chat_command(command,data){
	data.command = command
	chat_socket.send(JSON.stringify(data))
}
chat_connect()
window.btn_chat_send.onclick = e=>{
	var msg = window.input_chat_msg.value
	if(!msg){return}
	chat_command("send-message",{"txt":msg})
}