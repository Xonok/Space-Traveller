function update_ships(msg,blah,nr){
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
	f.headers(shipdiv,"img","ship","hull","armor","shield","drone","missile")
	q.battle.sides[nr].order.forEach(s=>{
		var drone = 0
		var missile = 0
		Object.entries(s.weapons).forEach(w=>{
			weapons_info[w[0]]=w[1]
			add(weapons,w[0],w[1].amount)
			if(w[1].type==="drone"){
				drone+=w[1].ammo
			}
			else if(w[1].type==="missile"){
				missile+=w[1].ammo
			}
		})
		s=s.ship
		var hull = s.stats.hull.current+"/"+s.stats.hull.max
		var armor = s.stats.armor.current+"/"+s.stats.armor.max
		var shield = s.stats.shield.current+"/"+s.stats.shield.max
		var img_box = document.createElement("div")
		img_box.classList.add("centered_")
		var img_div = f.addElement(img_box,"img")
		img_div.src = s.img
		var div_name = document.createElement("div")
		div_name.innerHTML = s.custom_name||s.type+"#"+s.id
		var tt_txt = ""
		tt_txt += "Ship type: "+q.ship_defs[s.type].name
		tt_txt += "<br>Owner: "+s.owner
		f.tooltip2(div_name,tt_txt)
		f.row(shipdiv,img_box,div_name,hull,armor,shield,drone,missile)
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
	Object.values(q.battle.sides[0]["missiles"]).forEach(dm=>{
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
	Object.values(q.battle.sides[1]["missiles"]).forEach(dm=>{
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
	window.missiles_ally.innerHTML+="<br><br> Retreat chance: "+String(Math.round(q.battle.sides[0].retreat_chance*100)/100)
	window.missiles_enemy.innerHTML+="<br><br> Retreat chance: "+String(Math.round(q.battle.sides[1].retreat_chance*100)/100)
}
function update_logs(msg){
	var sides = q.battle.sides
	if(q.battle_update){
		sides = q.battle_update.sides
	}
	
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
				f.addElement(ally_logs,"div",f.formatString(m.msg))
			})
			sides[1].logs[idx].forEach(m=>{
				f.addElement(enemy_logs,"div",f.formatString(m.msg))
			})
		})
		last_a && last_a.classList.add("box_focus")
		last_b && last_b.classList.add("box_focus")
	}
}
function update_result(msg){
	var attackers = Object.keys(q.battle.sides[0].combat_ships).length
	var defenders = Object.keys(q.battle.sides[1].combat_ships).length
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
function update_title(msg){
	var allies = []
	var enemies = []
	Object.values(q.battle.sides[0].combat_ships).forEach(cs=>{
		if(!allies.includes(cs.ship.owner)){
			allies.push(cs.ship.owner)
		}
	})
	Object.values(q.battle.sides[1].combat_ships).forEach(cs=>{
		if(!enemies.includes(cs.ship.owner)){
			enemies.push(cs.ship.owner)
		}
	})
	window.title_div.innerHTML = allies.join(", ")+" vs "+enemies.join(", ")
	window.round_div.innerHTML = "Round "+String(q.battle.round)
}
function row(parent,...data){
	var r = f.addElement(parent,"tr")
	data.forEach(d=>f.addElement(r,"td",d))
}
function do_attack(){
	f.send("attack")
}
function do_retreat(){
	f.send("retreat")
}
function do_leave(){
	f.send("retreat")
}
function battle_keydown(e){
	if(e.repeat){return}
	if(document.activeElement.nodeName === "INPUT"){return}
	if(e.code==="KeyA"){do_attack()}
	else if(e.code==="KeyR"){do_retreat()}
	else{return}
	e.preventDefault()
}


function battle_open(){
	window.retreat.onclick = do_retreat
	window.attack.onclick = do_attack
	window.leave.onclick = do_leave
	f.send("get-battle")
}
function battle_message(msg){
	if(!q.battle){
		f.view.open("nav")
		return
	}
	window.onkeydown = battle_keydown
	update_ships(msg,"ally",0)
	update_ships(msg,"enemy",1)
	update_missiles(msg)
	update_logs(msg)
	update_result(msg)
	update_title(msg)
}
f.view.register("battle",battle_open,battle_message)
