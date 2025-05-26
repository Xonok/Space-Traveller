/*
CODE STATUS - simple
Things work. Nothing in particular seems to be bad.
*Maybe this file should be moved into a separate folder.
*/

const key = localStorage.getItem("key")

func.init()
function send(command,table={}){
	table.command = command
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===400){
			window.error_display.innerHTML = e.target.response
		}
		else if(e.target.status===201){
			window.error_display.innerHTML = e.target.response
		}
		else if(e.target.status===200){
			localStorage.setItem("key",e.target.response)
			sessionStorage.removeItem("view_id")
			window.location.href = "/game.html"
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function get_args(username,password,password2=null){
	var user = window[username].value
	var pass = window[password].value
	var pass2 = password2 && window[password2].value
	if(!user){
		window.error_display.innerHTML = "Missing username."
		return
	}
	if(!pass){
		window.error_display.innerHTML = "Missing password."
		return 
	}
	if(password2 && pass!=pass2){
		window.error_display.innerHTML = "Passwords don't match."
		return 
	}
	return {
		"username":user,
		"password":pass
	}
}

function do_login(e){
	var a = get_args("username","password")
	if(!a){return}
	send("login",a)
}
function do_register(e){
	var a = get_args("rusername","rpassword","rpassword2")
	if(!a){return}
	send("register",a)
}
// 
function warningVisibility(){
	if(window.register_tab.classList.contains("register_login_active")){
		window.warning.style.display="initial"
		window.welcome_message.style.display="none"
	}
	else{
		window.warning.style.display="none"
		window.welcome_message.style.display="block"
	}
}
window.welcome_message.innerHTML = key ? "Welcome (back). You fill out these </br>forms, i'll go get the keys to your </br>ship(s)." : "First time?"
window.login_register.onclick=warningVisibility
window.login.onclick = do_login
window.register.onclick = do_register
window.username.focus()
window.username.addEventListener("keypress",(event=>{event.key==="Enter" && window.password.focus()}))
window.password.addEventListener("keypress",(event=>{event.key==="Enter" && window.login.click()}))