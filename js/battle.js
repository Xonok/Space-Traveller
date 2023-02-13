const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.retreat.onclick = do_retreat
window.attack.onclick = do_attack

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
			update_enemies(msg)
			update_allies_weapons(msg)
			update_enemies_weapons(msg)
			update_log(msg)
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
function update_allies_weapons(msg){
	window.ally_stats.innerHTML=""
	var parent = window.ally_stats
	var i=0
	var total_managers=0
	var emootional_daamage=0
	for(let [key,value] of Object.entries(msg.ally_weapons)){
		i+=value.count
		window.ally_stats.innerHTML+="</br>"+value.name+" x"+value.count
		total_managers+=value.shots*value.count
		emootional_daamage+=value.shots*value.count*value.damage
	}
	window.ally_stats.innerHTML+="</br></br> Total weapons: "+i
	window.ally_stats.innerHTML+="</br> Total attacks: "+total_managers
	window.ally_stats.innerHTML+="</br> Maximum damage: "+emootional_daamage
}
function update_enemies_weapons(msg){
	window.enemy_stats.innerHTML=""
	var i=0
	var total_Karens=0
	var emootional_daamage=0
	Object.values(msg.enemy_weapons).forEach(w=>{
		i+=w.count
		window.enemy_stats.innerHTML+="</br>"+w.name+" x"+w.count
		total_Karens+=w.shots*w.count
		emootional_daamage+=w.shots*w.count*w.damage
	})
	window.enemy_stats.innerHTML+="</br></br> Total weapons: "+i
	window.enemy_stats.innerHTML+="</br> Total attacks: "+total_Karens
	window.enemy_stats.innerHTML+="</br> Maximum damage: "+emootional_daamage
}
function update_allies(msg){
	var parent = window.ally_ships
	parent.innerHTML = ""
	headers(parent,"owner","ship")
	Object.values(msg.allies).forEach(s=>{
		row(parent,s.owner,s.name)
	})
}
function update_enemies(msg){
	var parent = window.enemy_ships
	parent.innerHTML = ""
	headers(parent,"owner","ship")
	Object.values(msg.enemies).forEach(s=>{
		row(parent,s.owner,s.custom_name || s.name)
	})
}
function update_log(msg){
	var parent = window.log
	parent.innerHTML = ""
	Object.values(msg.battle.logs.reverse()).forEach(v=>{
		addElement(parent,"label",v)
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

function do_attack(){
	send("attack",{"rounds":1})
}
function do_retreat(){
	send("retreat")
}

send("update-battle")