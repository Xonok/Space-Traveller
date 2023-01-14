const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

function send(command,table={}){
	table.key = key
	table.command = command
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url
				return
			}
			var msg = JSON.parse(e.target.response)
			console.log(msg)
			update_allies(msg)
			update_foes(msg)
		}
		else if(e.target.status===400){
			window.error_display.innerHTML = e.target.response
			console.log(e.target.response)
		}
		else if(e.target.status===400){
			window.error_display.innerHTML = "Server error."
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function update_allies(msg){
	var parent = window.ally_ships
	parent.innerHTML = ""
	headers(parent,"owner","ship")
	Object.values(msg.ships).forEach(s=>{
		row(parent,s.owner,s.name)
	})
}
function update_foes(msg){
	var parent = window.foe_ships
	parent.innerHTML = ""
	headers(parent,"owner","ship")
	Object.values(msg.eships).forEach(s=>{
		row(parent,s.owner,s.custom_name || s.name)
	})
}
function addElement(parent,type,inner){
	var e = document.createElement(type)
	if(inner!==undefined){e.innerHTML=inner}
	parent.append(e)
	return e
}
function headers(parent,...names){
	names.forEach(n=>addElement(parent,"th",n))
}
function row(parent,...data){
	var r = addElement(parent,"tr")
	data.forEach(d=>addElement(r,"td",d))
}
function forClass(name,func){
	Array.from(document.getElementsByClassName(name)).forEach(func)
}

send("update-battle")