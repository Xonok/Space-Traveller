function send(table){
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.send(jmsg)
}
function get_args(){
	var user = window.username.value
	var pass = window.password.value
	if(!user){
		window.error_display.innerHTML = "Missing username."
		return
	}
	if(!pass){
		window.error_display.innerHTML = "Missing password."
		return 
	}
	return {
		"username":user,
		"password":pass
	}
}

function do_login(e){
	var a = get_args()
	if(!a){return}
	send(Object.assign({"command":"login"},a))
}
function do_register(e){
	var a = get_args()
	if(!a){return}
	send(Object.assign({"command":"register"},a))
}

window.login.onclick = do_login
window.register.onclick = do_register