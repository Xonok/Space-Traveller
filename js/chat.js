var chat_socket
var last_message_idx = {}

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
			return
		}
		if(evt === "error"){
			var idx = last_message_idx[chat_active_channel]
			display_msg(chat_active_channel,[idx,Date.now()/1000,"Server","Server",msg.txt])
		}
		if(evt === "auth-done"){
			chat_command("get-channels")
		}
		if(evt === "channels-receive"){
			setup_channels(msg.data)
			msg.data.forEach(channel=>{
				var last_idx = last_message_idx[channel]
				if(last_idx === undefined){
					last_idx = -1
				}
				chat_command("get-messages",{"channel":channel,"idx":last_idx})
			})
		}
		if(evt === "auth-fail"){
			console.log("Chat auth failed. Disconnecting.")
			should_close = true
			chat_socket.close()
		}
		if(evt === "msg-receive"){
			last_message_idx[msg.channel] = msg.idx
			display_msg(msg.channel,msg.data)
		}
		if(evt === "msg-receive-multi"){
			last_message_idx[msg.channel] = msg.idx
			msg.data.forEach(d=>{
				display_msg(msg.channel,d)
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
function chat_command(command,data={}){
	data.command = command
	chat_socket.send(JSON.stringify(data))
}
var chat_channels = {}
var chat_active_channel
function setup_channels(channels){
	channels.forEach(c=>{
		if(!chat_channels[c]){
			var el = f.addElement(window.chat_log,"table")
			el.style.paddingBottom = "0"
			chat_channels[c] = el
			el.style.display = "none"
			var btn = f.addElement(window.chat_channel_buttons,"button",c)
			btn.onclick = ()=>{
				window.input_chat_msg.value = ""
				chat_active_channel = c
				chat_channels.forEach((name,div)=>{
					div.style.display = chat_active_channel === name ? "initial" : "none"
				})
				window.chat_log.scrollTop = window.chat_log.scrollHeight
			}
			if(!chat_active_channel){
				btn.click()
				window.input_chat_msg.style.display = "initial"
				window.btn_chat_send.style.display = "initial"
			}
		}
	})
	
}
function display_msg(channel,data){
	var [idx,time,user,char,txt] = data
	var date = new Date(time*1000)
	var date_days = date.toLocaleString(func.getSetting("locale")||navigator.languages,{month:"numeric",day:"numeric"})
	var date_clock = date.toLocaleString(func.getSetting("locale")||navigator.languages,{hour:"numeric",minute:"numeric"})
	var date_txt = date_days+":"+date_clock
	var div_date = f.createElement("div",date_txt)
	var div_sender = f.createElement("div",user)
	var div_txt = f.createElement("div",txt)
	var scrolled_down = window.chat_log.scrollHeight-window.chat_log.scrollTop <= window.chat_log.clientHeight+1
	f.row(chat_channels[channel],div_date,div_sender,div_txt)
	if(scrolled_down){
		window.chat_log.scrollTop = window.chat_log.scrollHeight
	}
}
var chat_init_done
function chat_update(view_id){
	var allowed_views = ["dock","nav","battle","map"]
	var should_show = allowed_views.includes(view_id) ? true : false
	window.box_chat.style.display = should_show ? "initial" : "none"
	if(chat_init_done){return}
	chat_init_done = true
	chat_connect()
}
window.btn_chat_send.onclick = e=>{
	var msg = window.input_chat_msg.value
	if(!msg){return}
	window.input_chat_msg.value = ""
	chat_command("send-message",{"channel":chat_active_channel,"txt":msg})
}
window.input_chat_msg.onkeydown = e=>{
	if(e.code === "Enter"){
		e.stopPropagation()
		e.preventDefault()
		window.btn_chat_send.click()
	}
}