/*
CODE STAGE - simple
This file might benefit from being split up and made to use standard parts.
However, it's concise and readable, so there is no rush.
*/

var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.retreat.onclick = do_retreat
window.attack.onclick = do_attack
window.leave.onclick = do_leave

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
			update_ships(msg,"ally",0)
			update_ships(msg,"enemy",1)
			update_missiles(msg)
			update_logs(msg)
			update_result(msg)
		}
		else if(e.target.status===400 || e.target.status===500){
			window.error_display.innerHTML = e.target.response
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function update_ships(msg,blah,nr){
	var cdata = msg.cdata
	var battle = msg.battle
	var weapons_info={}
	const add = (list,item,amount)=>{
		if(!list[item]){list[item] = 0}
		list[item] += amount
	}
	//ally
	var weapons = {}
	var drones = {}
	var shipdiv = window["ships_"+blah]
	var statdiv = window["stats_"+blah]
	var missdiv = window["missiles_"+blah]
	shipdiv.innerHTML = ""
	statdiv.innerHTML = ""
	missdiv.innerHTML = ""
	f.headers(shipdiv,"owner","ship","hull","armor","shield")
	Object.values(msg.battle.sides[nr].combat_ships).forEach(s=>{
		Object.entries(s.weapons).forEach(w=>{
			weapons_info[w[0]]=w[1]
			add(weapons,w[0],w[1].amount)
		})
		s=s.ship
		var hull = s.stats.hull.current+"/"+s.stats.hull.max
		var armor = s.stats.armor.current+"/"+s.stats.armor.max
		var shield = s.stats.shield.current+"/"+s.stats.shield.max
		row(shipdiv,s.owner,s.custom_name||s.type+"#"+s.id,hull,armor,shield)
	})
	var weapon_count = 0
	var attacks = 0
	var damage = 0
	Object.entries(weapons).forEach(w=>{
		var name = w[0]
		var count = w[1]
		weapon_count += count
		attacks += count*weapons_info[name].shots
		damage += count*weapons_info[name].shots*weapons_info[name].damage
		statdiv.innerHTML+="</br>"+weapons_info[name].name+" x"+count
	})
	statdiv.innerHTML+="<br></br> Total weapons: "+weapon_count
	statdiv.innerHTML+="<br> Total attacks: "+attacks
	statdiv.innerHTML+="<br> Maximum damage: "+damage
}
function update_missiles(msg){
	window.missiles_ally.innerHTML = ""
	window.missiles_enemy.innerHTML = ""
	var ally_drones = 0
	var ally_missiles = 0
	var enemy_drones = 0
	var enemy_missiles = 0
	Object.values(msg.battle.sides[0]["drones/missiles"]).forEach(dm=>{
		switch(dm.subtype){
			case "drone":
				ally_drones++
				break
			case "missile":
				ally_missiles++
				break
			default:
				throw new Error(dm.subtype)
		}
	})
	Object.values(msg.battle.sides[1]["drones/missiles"]).forEach(dm=>{
		switch(dm.subtype){
			case "drone":
				enemy_drones++
				break
			case "missile":
				enemy_missiles++
				break
			default:
				throw new Error(dm.subtype)
		}
	})
	f.addElement(window.missiles_ally,"div","Drones: "+ally_drones)
	f.addElement(window.missiles_ally,"div","Missile: "+ally_missiles)
	f.addElement(window.missiles_enemy,"div","Drones: "+enemy_drones)
	f.addElement(window.missiles_enemy,"div","Missile: "+enemy_missiles)
	window.missiles_ally.innerHTML+="<br><br> Retreat chance: "+String(Math.round(msg.battle.sides[0].retreat_chance*100)/100)
	window.missiles_enemy.innerHTML+="<br><br> Retreat chance: "+String(Math.round(msg.battle.sides[1].retreat_chance*100)/100)
}
function update_logs(msg){
	var sides = msg.battle.sides
	f.forClass("box_focus",e=>e.classList.remove("box_focus"))
	if(sides[0].logs){
		var last_a
		var last_b
		sides[0].logs.forEach((l,idx)=>{
			var parent = window.logs
			var row = f.addElement(parent,"tr",null,true)
			var ally_logs = f.addElement(row,"td")
			var enemy_logs = f.addElement(row,"td")
			ally_logs.classList.add("box")
			enemy_logs.classList.add("box")
			last_a = ally_logs
			last_b = enemy_logs
			l.forEach(m=>{
				f.addElement(ally_logs,"div",m.msg)
			})
			sides[1].logs[idx].forEach(m=>{
				f.addElement(enemy_logs,"div",m.msg)
			})
		})
		last_a && last_a.classList.add("box_focus")
		last_b && last_b.classList.add("box_focus")
	}
	else{
		var parent = window.logs
		var row = f.addElement(parent,"tr",null,true)
		var ally_logs = f.addElement(row,"td")
		var enemy_logs = f.addElement(row,"td")
		ally_logs.classList.add("box")
		enemy_logs.classList.add("box")
		ally_logs.classList.add("box_focus")
		enemy_logs.classList.add("box_focus")
		sides[0].last_log.forEach(m=>{
			f.addElement(ally_logs,"div",m.msg)
		})
		sides[1].last_log.forEach(m=>{
			f.addElement(enemy_logs,"div",m.msg)
		})
	}
}
function update_result(msg){
	var attackers = Object.keys(msg.battle.sides[0].combat_ships).length
	var defenders = Object.keys(msg.battle.sides[1].combat_ships).length
	if(!attackers && !defenders){
		window.result_message.innerHTML = "Draw."
	}
	else if(!attackers){
		window.result_message.innerHTML = "Defeat..."
	}
	else if (!defenders){
		window.result_message.innerHTML = "Victory!"
	}
	var combat_over = !attackers || !defenders
	window.retreat.style.visibility = combat_over ? "hidden" : "visible"
	window.attack.style.visibility = combat_over ? "hidden" : "visible"
	window.leave.style.visibility = !combat_over ? "hidden" : "visible"
}
function row(parent,...data){
	var r = f.addElement(parent,"tr")
	data.forEach(d=>f.addElement(r,"td",d))
}
function do_attack(){
	send("attack",{"rounds":1})
}
function do_retreat(){
	send("retreat")
}
function do_leave(){
	send("retreat")
}

send("update-battle")