var chat_socket
var last_message_idx = -1

function chat_connect(){
	chat_socket = new WebSocket("wss://"+location.host+"/chat_async")
	var should_close = false
	
	chat_socket.onopen = e=>{
		console.log(e)
		// chat_socket.send(JSON.stringify({"msg":"hello"}))
		var key = localStorage.getItem("key")
		chat_command("auth",{key})
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
		if(evt === "auth-done"){
			chat_command("get-messages",{"idx":last_message_idx})
		}
		if(evt === "auth-fail"){
			console.log("Chat auth failed. Disconnecting.")
			should_close = true
			chat_socket.close()
		}
		if(evt === "msg-receive"){
			display_msg(msg.data)
		}
		if(evt === "msg-receive-multi"){
			msg.data.forEach(d=>{
				display_msg(d)
			})
		}
	}
	chat_socket.onerror = e=>{
		!should_close && chat_socket.close()
	}
	chat_socket.onclose = e=>{
		setTimeout(chat_connect,1000)
	}
}
function chat_command(command,data){
	data.command = command
	chat_socket.send(JSON.stringify(data))
}
function display_msg(data){
	var date = new Date(data.time*1000)
	var date_days = date.toLocaleString(func.getSetting("locale")||navigator.languages,{month:"numeric",day:"numeric"})
	var date_clock = date.toLocaleString(func.getSetting("locale")||navigator.languages,{hour:"numeric",minute:"numeric"})
	var date_txt = date_days+":"+date_clock
	var div_date = f.createElement("div",date_txt)
	var div_sender = f.createElement("div",data.sender)
	var div_txt = f.createElement("div",data.txt)
	f.row(window.chat_log,div_date,div_sender,div_txt)
}
chat_connect()
window.btn_chat_send.onclick = e=>{
	var msg = window.input_chat_msg.value
	if(!msg){return}
	chat_command("send-message",{"txt":msg})
}