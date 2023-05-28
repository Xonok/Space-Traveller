config.apply()
var f = func
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
			update_log(msg,window.log_ally,0)
			update_log(msg,window.log_enemy,1)
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
	var weapons={}
	const add = (list,item,amount)=>{
		if(!list[item]){list[item] = 0}
		list[item] += amount
	}
	//ally
	var ally_weapons = {}
	var ally_drones = {}
	window.ally_ships.innerHTML = ""
	window.ally_stats.innerHTML = ""
	window.missile_ally.innerHTML = ""
	f.headers(window.ally_ships,"owner","ship","hull","armor","shield")
	// Object.values(msg.battle.sides[0].drones/missiles).forEach(d=>{
		
	// })
	Object.values(msg.battle.sides[0].combat_ships).forEach(s=>{
		Object.entries(s.weapons).forEach(w=>{
			weapons[w[0]]=w[1]
			add(ally_weapons,w[0],w[1].amount)
		})
		s=s.ship
		var hull = s.stats.hull.current+"/"+s.stats.hull.max
		var armor = s.stats.armor.current+"/"+s.stats.armor.max
		var shield = s.stats.shield.current+"/"+s.stats.shield.max
		row(window.ally_ships,s.owner,s.custom_name||s.name,hull,armor,shield)
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
	window.ally_stats.innerHTML+="</br></br> Total weapons: "+ally_weapon_count
	window.ally_stats.innerHTML+="</br> Total attacks: "+ally_attacks
	window.ally_stats.innerHTML+="</br> Maximum damage: "+ally_damage
	// window.missile_ally.innerHTML
	//enemy
	var enemy_weapons = {}
	window.enemy_ships.innerHTML = ""
	f.headers(window.enemy_ships,"owner","ship","hull","armor","shield")
	window.enemy_stats.innerHTML = ""
	window.missile_enemy.innerHTML = ""
	// Object.values(msg.battle.sides[0].drones/missiles).forEach(d=>{
	
	// })
	Object.values(msg.battle.sides[1].combat_ships).forEach(s=>{
		Object.entries(s.weapons).forEach(w=>{
			weapons[w[0]]=w[1]
			add(enemy_weapons,w[0],w[1].amount)
		})
		s=s.ship
		var hull = s.stats.hull.current+"/"+s.stats.hull.max
		var armor = s.stats.armor.current+"/"+s.stats.armor.max
		var shield = s.stats.shield.current+"/"+s.stats.shield.max
		row(window.enemy_ships,s.owner,s.custom_name||s.name,hull,armor,shield)
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
	window.enemy_stats.innerHTML+="</br></br> Total weapons: "+enemy_weapon_count
	window.enemy_stats.innerHTML+="</br> Total attacks: "+enemy_attacks
	window.enemy_stats.innerHTML+="</br> Maximum damage: "+enemy_damage
	// window.missile_enemy.innerHTML
}
function update_log(msg,parent,number){
	parent.innerHTML = ""
	Object.values(msg.battle.sides[number].logs?.reverse()).forEach(v=>{
		v.forEach(m=>f.addElement(parent,"label",m.msg))
		
	})
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

send("update-battle")