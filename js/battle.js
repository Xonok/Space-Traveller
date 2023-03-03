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
			update_ships(msg)
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
function update_ships(msg){
	var cdata = msg.cdata
	var battle = msg.battle
	var weapons = msg.weapons
	var attackers = battle.attackers
	var defenders = battle.defenders
	var ally_weapons = {}
	var enemy_weapons = {}
	const add = (list,item,amount)=>{
		if(!list[item]){list[item] = 0}
		list[item] += amount
	}
	window.ally_ships.innerHTML = ""
	window.enemy_ships.innerHTML = ""
	headers(window.ally_ships,"owner","ship")
	headers(window.enemy_ships,"owner","ship")
	window.ally_stats.innerHTML = ""
	window.enemy_stats.innerHTML = ""
	Object.values(msg.ships).forEach(s=>{
		if(cdata.ships.includes(s.name)){
			if(attackers.includes(s.name) || defenders.includes(s.name)){
				row(window.ally_ships,s.owner,s.custom_name||s.name)
			}
			Object.entries(s.inventory.gear).forEach(i=>{
				if(weapons[i[0]]){
					add(ally_weapons,i[0],i[1])
				}
			})
		}
		else{
			if(attackers.includes(s.name) || defenders.includes(s.name)){
				row(window.enemy_ships,s.owner,s.custom_name||s.name)
			}
			Object.entries(s.inventory.gear).forEach(i=>{
				if(weapons[i[0]]){
					add(enemy_weapons,i[0],i[1])
				}
			})
		}
	})
	var ally_weapon_count = 0
	var ally_attacks = 0
	var ally_damage = 0
	Object.entries(ally_weapons).forEach(w=>{
		var name = w[0]
		var count = w[1]
		ally_weapon_count += count
		ally_attacks += count*weapons[name].shots
		ally_damage += count*weapons[name].shots*weapons[name].damage
		window.ally_stats.innerHTML+="</br>"+weapons[name].name+" x"+count
	})
	var enemy_weapon_count = 0
	var enemy_attacks = 0
	var enemy_damage = 0
	Object.entries(enemy_weapons).forEach(w=>{
		var name = w[0]
		var count = w[1]
		enemy_weapon_count += count
		enemy_attacks += count*weapons[name].shots
		enemy_damage += count*weapons[name].shots*weapons[name].damage
		window.enemy_stats.innerHTML+="</br>"+weapons[name].name+" x"+count
	})
	window.ally_stats.innerHTML+="</br></br> Total weapons: "+ally_weapon_count
	window.ally_stats.innerHTML+="</br> Total attacks: "+ally_attacks
	window.ally_stats.innerHTML+="</br> Maximum damage: "+ally_damage
	window.enemy_stats.innerHTML+="</br></br> Total weapons: "+enemy_weapon_count
	window.enemy_stats.innerHTML+="</br> Total attacks: "+enemy_attacks
	window.enemy_stats.innerHTML+="</br> Maximum damage: "+enemy_damage
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