var chat_socket
var last_message_idx = {}

var chat_prev_group
query.register(get_group_chat,"group")
function get_group_chat(){
	if(!chat_prev_group && !q.group){return}
	if(q.group?.id === chat_prev_group){return}
	if(!chat_auth_done){return}
	if(!q.group || (chat_prev_group && q.group.id !== chat_prev_group)){
		chat_channels[chat_prev_group].btn.style.display = "none"
		if(chat_active_channel === chat_prev_group){
			chat_channels[Object.keys(chat_channels)[0]].btn.click()
		}
	}
	chat_prev_group = q.group?.id
	if(q.group){
		setup_channels({[q.group.id]:q.group.name})
		chat_channels[q.group.id].btn.style.display = "initial"
		var last_idx = last_message_idx[q.group.id]
		if(last_idx === undefined){
			last_idx = -1
		}
		chat_command("get-messages",{"channel":q.group.id,"idx":last_idx,"char":q.cdata.name})
	}
}
var chat_auth_done = false
function chat_connect(){
	var protocol = location.protocol === "https:" ? "wss://" : "ws://"
	var key = localStorage.getItem("key")
	chat_socket = new WebSocket(protocol+location.host+"/chat_async?key="+key)
	var should_close = false
	chat_auth_done = false
	
	chat_socket.onopen = e=>{
		console.log("Websocket connected.")
		// console.log(e)
		// var key = localStorage.getItem("key")
		// chat_command("auth",{key})
	}
	chat_socket.onmessage = e=>{
		var msg = JSON.parse(e.data)
		var evt = msg.event
		var data = msg.data
		// console.log(e,evt,data)
		if(!evt){
			return
		}
		if(evt === "error"){
			console.log(msg)
			var idx = last_message_idx[chat_active_channel]
			display_msg(chat_active_channel,[idx,Date.now()/1000,"Server","Server",msg.txt],true)
		}
		if(evt === "auth-done"){
			chat_auth_done = true
			chat_command("get-ship-positions")
			chat_command("get-channels")
		}
		if(evt === "channels-receive"){
			setup_channels(msg.data)
			msg.data.forEach(channel=>{
				var last_idx = last_message_idx[channel]
				if(last_idx === undefined){
					last_idx = -1
				}
				chat_command("get-messages",{"channel":channel,"idx":last_idx,"char":q.cdata.name})
			})
			if(q.cdata){
				get_group_chat()
			}
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
		if(evt === "receive-ship-positions"){
			query.receive(data)
			nav.map.should_draw = true
		}
		if(evt === "update-ship-positions"){
			var start = nav.map.localTime(data.start_time)
			var end = nav.map.localTime(data.end_time)
			data.positions.forEach((sname,data)=>{
				var pos = q.positions[sname] || {}
				var moving = q.moving[sname] || {x:pos.x,y:pos.y,r:pos.rotation,start}
				moving.x2 = data.x
				moving.y2 = data.y
				moving.r2 = data.rotation
				moving.end = Math.max(Date.now()/1000+0.1,end)
				q.moving[sname] = moving
				pos.x = data.x
				pos.y = data.y
				pos.rotation = data.rotation
				q.positions[sname] = pos
			})
			nav.map.should_draw = true
		}
		if(evt === "remove-ships"){
			data.snames.forEach(sname=>{
				delete q.positions[sname]
			})
			nav.map.should_draw = true
		}
		if(evt === "add-ships"){
			data.positions.forEach((sname,data)=>{
				q.positions[sname] = data
			})
			nav.map.should_draw = true
		}
	}
	chat_socket.onerror = e=>{
		console.log(e)
		!should_close && chat_socket.close()
	}
	chat_socket.onclose = e=>{
		console.log("WebSocket closed, retrying in 1 second.")
		setTimeout(chat_connect,1000)
	}
}
function chat_command(command,data={}){
	if(!chat_socket){
		console.log("Skipping chat command "+command+" because the socket isn't connected yet.")
		return
	}
	data.command = command
	chat_socket.send(JSON.stringify(data))
}
var chat_channels = {}
var chat_active_channel
function setup_channels(channels){
	channels.forEach((c,name)=>{
		if(!chat_channels[c]){
			var el = f.addElement(window.chat_log,"table")
			el.style.paddingBottom = "0"
			chat_channels[c] = el
			el.style.display = "none"
			var btn = f.addElement(window.chat_channel_buttons,"button",name)
			el.btn = btn
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
function display_msg(channel,data,error=false){
	var [idx,time,user,char,txt] = data
	var date = new Date(time*1000)
	var date_days = date.toLocaleString(func.getSetting("locale")||navigator.languages,{month:"numeric",day:"numeric"})
	var date_clock = date.toLocaleString(func.getSetting("locale")||navigator.languages,{hour:"numeric",minute:"numeric"})
	var date_txt = date_days+":"+date_clock
	var div_date = f.createElement("div",date_txt)
	var div_sender = f.createElement("div",user)
	var div_txt = f.createElement("div",txt)
	if(error){
		div_txt.style.color = "red"
		div_txt.innerHTML = "<b>"+div_txt.innerHTML+"</b>"
	}
	var scrolled_down = window.chat_log.scrollHeight-window.chat_log.scrollTop <= window.chat_log.clientHeight+1
	f.row(chat_channels[channel],div_date,div_sender,div_txt)
	if(scrolled_down){
		window.chat_log.scrollTop = window.chat_log.scrollHeight
	}
}
var chat_prev_cdata
function chat_update(view_id){
	var allowed_views = ["dock","nav","battle","map"]
	var should_show = allowed_views.includes(view_id) ? true : false
	window.box_chat.style.display = should_show ? "initial" : "none"
	if(chat_prev_cdata?.name !== q.cdata?.name){
		chat_command("get-ship-positions")
	}
	chat_prev_cdata = q.cdata
}
var chat_init_done
function chat_init(){
	if(chat_init_done){return}
	if(!q.cdata){
		console.log("cdata not yet ready, so chat can't start.")
		return
	}
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