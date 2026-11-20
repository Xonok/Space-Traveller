var net = {
	post(data,handler){
		var req = new XMLHttpRequest()
		req.open("POST",window.location.href,true)
		req.onload = handler
		req.send(data)
	},
	post_json(data,handler){
		var jmsg = JSON.stringify(data)
		net.post(jmsg,handler)
	}
}
