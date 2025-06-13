nav.ship = {
	update_vitals(){
		var tab = "&nbsp;&nbsp;&nbsp;&nbsp;"
		var {hull,armor,shield} = q.pship.stats
		var xp_percent = Math.round(q.cdata.xp/10)
		window.vitals.innerHTML = "Level: "+q.cdata.level+" ("+xp_percent+"%)"+tab
		window.vitals.innerHTML += "Hull: "+hull.current+"/"+hull.max+tab
		window.vitals.innerHTML += "Armor: "+armor.current+"/"+armor.max+tab
		window.vitals.innerHTML += "Shield: "+shield.current+"/"+shield.max
	},
	update_ships(){
		nav.ship.update_vitals()
		var ships = window.ships
		var own_ships = window.own_ships
		var own_guards = window.own_guards
		ships.innerHTML=""
		own_ships.innerHTML = ""
		own_guards.innerHTML = ""
		var ship_names=Object.values(q.tile.ships)
		var stranger = ship_names.find(p=>p.find(s=>s.owner !== q.cdata.name))
		var follower = ship_names.find(p=>p.find(s=>q.cdata.ships.includes(s.name)))
		var guarding = ship_names.find(p=>p.find(s=>s.owner === q.cdata.name && !q.cdata.ships.includes(s.name)))
		window.empty_ships.style = (stranger || q.map_structure.name || q.tile.wormhole) ? "display:none" : "display:initial"
		window.empty_follower.style = follower ? "display:none" : "display:initial"
		window.empty_guard.style = guarding ? "display:none" : "display:initial"
		var other_ships = {}
		var own_following = {}
		var own_guarding = {}
		var own_threat = 0
		for(let tships of Object.values(q.tile.ships)){
			tships.forEach(s=>{
				if(s.owner !== q.cdata.name){
					other_ships[s.name] = s
				}
				else if(q.cdata.ships.includes(s.name)){
					own_following[s.name] = s
					own_threat += s.threat
				}
				else{
					own_guarding[s.name] = s
				}
			})
		}
		window.fleet_label.innerHTML = "Fleet (threat "+own_threat+")"
		window.fleet_command.innerHTML = "Command: "+q.cdata.command_battle_used+"/"+q.cdata.command_freight_used+"/"+q.cdata.command_max
		var battle_penalty = (q.cdata.command_battle_used / q.cdata.command_max)**2
		var freight_penalty = (q.cdata.command_freight_used / (q.cdata.command_max+q.cdata.command_freight_bonus))**2
		battle_penalty = battle_penalty === Infinity ? 5 : battle_penalty
		freight_penalty = freight_penalty === Infinity ? 5 : freight_penalty
		
		var desc_long = ""
		desc_long += "Battle: "+q.cdata.command_battle_used+"/"+q.cdata.command_max
		desc_long += battle_penalty <= 1 || isNaN(battle_penalty) ? " no penalties" : " penalty *"+Math.floor(1/battle_penalty*100)/100
		desc_long += "<br>Freight: "+q.cdata.command_freight_used+"/"+(q.cdata.command_max+q.cdata.command_freight_bonus)
		desc_long += freight_penalty <= 1 || isNaN(freight_penalty) ? " no penalties" : " penalty *"+Math.floor(1/freight_penalty*100)/100
		func.tooltip2(window.fleet_command,desc_long)
		
		if(q.map_structure.name){
			other_ships[q.map_structure.name] = q.map_structure
		}
		var wh = q.tile.wormhole
		if(wh){
			other_ships[wh.name] = Object.assign({},wh)
			other_ships[wh.name].name = "Gate to "+wh.target.system
			other_ships[wh.name].wormhole = true
		}
		
		var t = f.make_table(window.ships,"img","name","threat","command")
		t.format("name",e=>f.shipName(e,"stranger"))
		t.sort("name","!structure")
		t.max_chars("name",24)
		t.add_tooltip2("name",data=>{
			var txt = ""
			txt += "Name: "+data.name+"<br>"
			txt += "Ship: "+data.ship+"<br>"
			txt += "Owner: "+data.owner+"<br>"
			if(data.threat !== undefined){
				txt += "Threat: "+(data.threat || 0)+"<br>"
			}
			return txt
		})
		t.add_class("command","full_btn")
		t.add_button("command","Attack",null,r=>f.send("start-battle",{"target":r.name}))
		attack_target = null
		t.for_col("command",(div,r,name)=>{
			if(other_ships[name].player === false && !other_ships[name].structure){
				div.innerHTML = "Attack"
				if(!attack_target){
					div.innerHTML = "Attack(K)"
					attack_target = r.name
				}
			}
			if(other_ships[name].structure){
				div.innerHTML = "Dock(d)"
				div.onclick = ()=>{
					f.view.open("dock")
				}
			}
			if(other_ships[name].wormhole){
				div.innerHTML = "Jump(i)"
				div.onclick = ()=>{
					f.send("jump")
				}
			}
			if(other_ships[name].player){
				div.remove()
			}
		})
		t.update(other_ships)
		
		var t2 = f.make_table(window.own_ships,"img","name","command")
		t2.format("name",e=>f.shipName(e,"character"))
		//t2.sort("name")
		t2.max_chars("name",24)
		t2.add_class("name","full_btn")
		t2.add_class("name","align_left")
		t2.add_tooltip2("name",data=>{
			var shipdef = q.idata[data.type]
			var stats = q.pships[data.name].stats
			var txt = ""
			txt += "Ship: "+shipdef.name+"<br>"
			txt += "Threat: "+data.threat+"<br>"
			txt += "Room: "+stats.room.current+"/"+stats.room.max+"<br>"
			txt += "Freight slots used: "+(shipdef.freight||0)+"<br>"
			txt += "Battle slots used: "+(shipdef.battle||0)+"<br>"
			return txt
		})
		t2.add_class("command","full_btn")
		t2.add_button("name",null,null,r=>{
			q.pship = q.pships[r.name]
			localStorage.setItem("ship",r.name)
			update_inventory()
			nav.ship.update_ships()
		})
		t2.for_col("name",(div,r)=>{
			if(r.name === q.pship.name){
				var parent = div.parentNode
				var classes = div.classList
				var children = Array.from(div.childNodes)
				div.remove()
				var new_div = f.addElement(parent,"div",f.shipName(q.pship,"character"))
				new_div.classList.add(...classes)
				children.forEach(c=>{
					if(c.nodeName === "#text"){return}
					new_div.appendChild(c)
				})
			}
		})
		t2.add_button("command","guard",null,r=>f.send("guard",{"dship":r.name}))
		t2.update(own_following)
		
		var t3 = f.make_table(window.own_guards,"img","name","command")
		t3.format("name",e=>f.shipName(e,"character"))
		//t3.sort("name")
		t3.max_chars("name",24)
		t3.add_tooltip2("name",data=>{
			var shipdef = q.idata[data.type]
			var txt = ""
			txt += "Ship: "+shipdef.name+"<br>"
			txt += "Threat: "+data.threat+"<br>"
			txt += "Room: "+data.stats.room.current+"/"+data.stats.room.max+"<br>"
			return txt
		})
		t3.add_class("command","full_btn")
		t3.add_button("command","follow",null,r=>f.send("follow",{"dship":r.name}))
		t3.update(own_guarding)
	}
}

