function send(table){
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===401){
			window.error_display.innerHTML = e.target.response
		}
		else if(e.target.status===201){
			window.error_display.innerHTML = e.target.response
		}
		else if(e.target.status===200){
			localStorage.setItem("key",e.target.response)
			window.location.href = "/nav.html"
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
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