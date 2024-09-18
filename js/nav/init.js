/*
CODE STATUS - messy
*Many things should be split off into their own files.
*Table code needs to use standard functions, like some aldready do.
*Stations on the tile should be in hot ships near you, with a dock button.
However, server-side support is not there, so for now the dock button would work exactly like the navbar one.
*/

var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var ship_img
var vision = 0
var pship
var pships
var cdata
var quests
var position = [0,0]
var idata = {}
var structure = {}
var tile = {}
var hwr = {}
var characters = {}
var terrain_color = {
	"energy":"#00bfff",
	"space":"#000000",
	"nebula":"#ff0000",
	"asteroids":"#808080",
	"exotic":"#7cfc00",
	"phase":"#ffa500"
}
var terrain_color_name = {
	"energy": "LightBlue",
	"space": "Black",
	"nebula": "Red",
	"asteroids": "Grey",
	"exotic": "Green",
	"phase": "Yellow"
}

function invertColour(hex) {
	hex = hex.slice(1)
	if(hex.length === 3){hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2]}
	if(hex.length !== 6){throw new Error('Invalid HEX color.')}
	var r = parseInt(hex.slice(0, 2), 16),
		g = parseInt(hex.slice(2, 4), 16),
		b = parseInt(hex.slice(4, 6), 16);
	var invert=(r * 0.299 + g * 0.587 + b * 0.114) > 120
	return invert? '#000000': '#FFFFFF'
}

var hwr_timer
var prev_msg
var prev_msg_count = 0
var prev_error
var prev_error_count = 0
var move_delay_timer
var last_action_time = Date.now()
function send(command,table={}){
	table.key = key
	table.command = command
	if(pship && !table.ship){
		table.ship = pship.name
	}
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	var send_time = Date.now()/1000
	last_action_time = Date.now()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		var recv_time = Date.now()/1000
		var ping = recv_time-send_time
		if(e.target.status===200){
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url
				return
			}
			window.onkeydown = keyboard_move
			window.error_display.innerHTML = ""
			Array.from(document.getElementsByTagName("td")).forEach(e=>{
				e.style.backgroundColor = null
				if(e.coord_x !== 0 || e.coord_y !== 0){
					e.innerHTML = ""
				}
			})
			var msg = JSON.parse(e.target.response)
			console.log(msg)
			cdata = msg.cdata
			pship = msg.ships[cdata.ship]
			pships = msg.ships
			quests=cdata.quests
			var local_ship = localStorage.getItem("ship")
			if(local_ship){
				if(Object.keys(pships).includes(local_ship)){
					pship = msg.ships[local_ship]
				}
				else{
					localStorage.setItem("ship",pship.name)
				}
			}
			idata = msg["idata"]
			structure = msg["structure"]
			tile = msg["tile"]
			hwr = msg["hwr"]
			characters = msg["characters"]
			var msg_txt = ""
			msg.messages.forEach((m,mID)=>{
				msg_txt += f.formatString(m)
				if(mID+1 < msg.messages.length){
					msg_txt += "<br>"
				}
			})
			if(!msg_txt){
				prev_msg_count = 0
				prev_msg = undefined
			}
			else if(msg_txt === prev_msg){
				prev_msg_count++
				window.info_display.innerHTML = msg_txt+"("+prev_msg_count+")"
			}
			else{
				window.info_display.innerHTML = msg_txt
				prev_msg_count = 1
			}
			prev_msg = msg_txt
			
			update_starmap(msg)
			update_speed()
			if(Object.keys(hwr).length && Object.entries(cdata.quests_completed || {}).length >= 1){
				var worst
				Object.entries(hwr).forEach(e=>{
					var ship_name = e[0]
					var data = e[1]
					if(!worst || worst.seconds < data.seconds){
						worst = data
						worst.name = f.shipName(pships[ship_name],"character")
					}
				})
				window.hwr_name.innerHTML = "Homeworld: "+cdata.home
				window.hwr_charges.innerHTML = "Charges: "+worst.charges+"/"+worst.max_charges
				
				var time_left = ""
				time_left += worst.seconds >= 3600 ? Math.floor(worst.seconds/3600)+"h" : ""
				time_left += worst.seconds >= 60 ? Math.floor(worst.seconds/60)%60+"m" : ""
				time_left += Math.floor(worst.seconds)%60+"s"
				var hwr_status = worst.charges ? "Status: Ready" : "Status: ready in "+time_left
				hwr_status = worst.seconds === -1 ? "Status: "+worst.time_left : hwr_status
				window.hwr_status.innerHTML = hwr_status
				
				if(hwr_timer){
					clearTimeout(hwr_timer)
				}
				var seconds = worst.seconds
				if(worst.seconds !== -1){
					hwr_timer = setInterval(e=>{
						seconds--
						var time_left = ""
						time_left += seconds >= 3600 ? Math.floor(seconds/3600)+"h" : ""
						time_left += seconds >= 60 ? Math.floor(seconds/60)%60+"m" : ""
						time_left += Math.floor(seconds)%60+"s"
						
						if(seconds < 0){
							window.hwr_status.innerHTM = "Status: Ready"
							f.forClass("info_display",e=>{e.innerHTML = "<br>"+"Next tick in: now."})
							clearTimeout(hwr_timer)
						}
						else{
							if(worst.charges){
								window.hwr_status.innerHTML = "Status: "+time_left
							}
							else{
								window.hwr_status.innerHTML = "Status: ready in "+time_left
							}
						}
						
					},1000)
				}
				window.hwr_box.style.display = "flex"
			}
			else{
				window.hwr_box.style.display = "none"
			}
			var tiles = msg.tiles
			var {x,y,rotation} = pship.pos
			window.credit.innerHTML= "Credits: "+func.formatNumber(cdata.credits)
			var noun_constellation = config.rainbow ? "Neighbourhood: " : "Constellation: "
			window.constellation.innerHTML = noun_constellation + msg.constellation
			var noun_system = config.rainbow ? "Star: " : "System: "
			window.place.innerHTML = noun_system + pship.pos.system
			var noun_coords = config.rainbow ? "GPS: " : "Coordinates: "
			window.player_position.innerHTML = noun_coords + pship.pos.x + "," + pship.pos.y
			var noun_terrain = config.rainbow ? "Land: " : "Terrain: "
			window.tile_terrain.innerHTML = noun_terrain+msg.tile.terrain
			var noun_resource = config.rainbow ? "Shinies: " : "Resource: "
			if(msg.tile.resource){
				window.tile_resource_text.innerHTML = noun_resource+idata[msg.tile.resource]["name"]+"("+msg.tile.resource_amount+")"
				window.tile_resource_img.setAttribute("src",msg.idata[msg.tile.resource].img)
			}
			else{
				window.tile_resource_text.innerHTML = noun_resource+"none"
				window.tile_resource_img.removeAttribute("src")
			}
			var noun_structure = config.rainbow ? "House: " : "Structure: "
			if(msg["structure"].ship || msg["structure"].type){
				window.tile_structure.innerHTML = msg["structure"].ship ? noun_structure + msg["structure"].ship : noun_structure + msg["structure"].type
			}
			else{
				window.tile_structure.innerHTML = noun_structure+"none"
			}
			update_ships(msg)
			update_quests(quests)
			console.log(cdata)
			position = [x,y]
			if(msg.vision !== vision){
				nav.map.init(window.space_map,msg.vision)
			}
			vision = msg.vision
			nav.map.update(x,y,tiles)
			update_inventory()
			//buttons
			var buttons_visible = false
			for(let [btn,display] of Object.entries(msg.buttons)){
				if(display!=="none"){buttons_visible = true}
				window[btn].style = "display:"+display
			}
			window.actions_empty.style.display = buttons_visible ? "none" : ""
			//ship
			if(pship.img !== ship_img.src){
				ship_img.src = pship.img
			}
			ship_img.style = "transform: rotate("+String(rotation)+"deg);"
			//station
			if((Object.keys(msg.structure).length && msg.structure.img) || tile.img){
				ship_img.style.display = "none"
			}
			else{
				ship_img.style.display = "initial"
			}
			
			if(move_delay_timer){
				clearInterval(move_delay_timer)
				move_delay_timer = null
			}
			move_delay_timer = setInterval(()=>{
				var time_left = send_time-Date.now()/1000+msg.delay-ping/2
				window.move_timer.innerHTML = "Recharging engines: "+Math.floor(time_left*100)/100
				if(time_left < 0){
					window.move_timer.innerHTML = ""
					clearInterval(move_delay_timer)
					move_delay_timer = null
				}
			},100)
			resize()
			prev_error_count = 0
			prev_error = undefined
		}
		else if(e.target.status===400 || e.target.status===500){
			window.info_display.innerHTML = ""
			var err = e.target.response
			if(!err){
				prev_error_count = 0
				prev_error = undefined
			}
			else if(err === prev_error){
				prev_error_count++
				window.error_display.innerHTML = err+"("+prev_error_count+")"
			}
			else{
				window.error_display.innerHTML = err
				prev_error_count = 1
			}
			prev_error = err
			console.log(err)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function update_quests(quests){
	window.questlines.innerHTML=""
	if(!Object.entries(quests).length){
		window.questlines.innerHTML="<it>No quests active currently.</it>"
		window.questlines.style="color:lightblue;"
	}
	else{
		for (const [questname, info] of Object.entries(quests)) {
		window.questlines.innerHTML+=questname+"</br>"
		}
	}
}
function update_starmap(msg){
	window.starmap.innerHTML = ""
	var sm = msg.starmap
	var make_anchor = (txt)=>{
		if(txt){
			var el = document.createElement("a")
			el.href = "/map.html?star="+txt
			el.innerHTML = txt
			return el
		}
		return ""
	}
	f.row(window.starmap,make_anchor(sm.nw),make_anchor(sm.n),make_anchor(sm.ne))
	f.row(window.starmap,make_anchor(sm.w),make_anchor(pship.pos.system),make_anchor(sm.e))
	f.row(window.starmap,make_anchor(sm.sw),make_anchor(sm.s),make_anchor(sm.se))
}
function update_speed(){
	var spd = nav.fleet.speed()
	var clean = s=>Math.round(s*10)/10
	var mod = terrain[tile.terrain].move_cost
	window.fleet_speed.innerHTML = "Speed: "+clean(spd/mod)
	var slowest_ship
	var slowest_speed = 100000
	Object.values(pships).forEach(pship=>{
		if(pship.stats.speed < slowest_speed){
			slowest_ship = pship.custom_name ? pship.custom_name+","+pship.id : pship.name
			slowest_speed = pship.stats.speed
		}
	})
	var tt = f.addElement(window.fleet_speed,"span","Fleet speed: "+clean(spd)+"<br>Terrain modifier: "+mod+"<br>Slowest ship: "+slowest_ship+" ("+clean(slowest_speed)+")")
	tt.className = "tooltiptext"
}
function update_ships(msg){
	nav.ship.update_vitals()
	var ships = window.ships
	var own_ships = window.own_ships
	var own_guards = window.own_guards
	ships.innerHTML=""
	own_ships.innerHTML = ""
	own_guards.innerHTML = ""
	var ship_names=Object.values(msg.tile.ships)
	var stranger = ship_names.find(p=>p.find(s=>s.owner !== cdata.name))
	var follower = ship_names.find(p=>p.find(s=>cdata.ships.includes(s.name)))
	var guarding = ship_names.find(p=>p.find(s=>s.owner === cdata.name && !cdata.ships.includes(s.name)))
	window.empty_ships.style = (stranger || structure.name || tile.wormhole) ? "display:none" : "display:initial"
	window.empty_follower.style = follower ? "display:none" : "display:initial"
	window.empty_guard.style = guarding ? "display:none" : "display:initial"
	var other_ships = {}
	var own_following = {}
	var own_guarding = {}
	var own_threat = 0
	for(let tships of Object.values(msg.tile.ships)){
		tships.forEach(s=>{
			if(s.owner !== cdata.name){
				other_ships[s.name] = s
			}
			else if(cdata.ships.includes(s.name)){
				own_following[s.name] = s
				own_threat += s.threat
			}
			else{
				own_guarding[s.name] = s
			}
		})
	}
	window.fleet_label.innerHTML = "Fleet (threat "+own_threat+")"
	window.fleet_command.innerHTML = "Command: "+cdata.command_battle_used+"/"+cdata.command_freight_used+"/"+cdata.command_max
	var battle_penalty = cdata.command_battle_used / cdata.command_max
	var freight_penalty = cdata.command_freight_used / (cdata.command_max+cdata.command_freight_bonus)
	battle_penalty = battle_penalty === Infinity ? 5 : battle_penalty
	freight_penalty = freight_penalty === Infinity ? 5 : freight_penalty
	
	var desc_long = ""
	desc_long += "Battle: "+cdata.command_battle_used+"/"+cdata.command_max
	desc_long += battle_penalty <= 1 || isNaN(battle_penalty) ? " no penalties" : " penalty *"+Math.floor(1/battle_penalty*100)/100
	desc_long += "<br>Freight: "+cdata.command_freight_used+"/"+(cdata.command_max+cdata.command_freight_bonus)
	desc_long += freight_penalty <= 1 || isNaN(freight_penalty) ? " no penalties" : " penalty *"+Math.floor(1/freight_penalty*100)/100
	func.tooltip2(window.fleet_command,desc_long)
	
	if(structure.name){
		other_ships[structure.name] = structure
	}
	var wh = tile.wormhole
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
		txt += "Name: "+(data.custom_name||data.name)+"<br>"
		txt += "Ship: "+data.ship+"<br>"
		txt += "Owner: "+data.owner+"<br>"
		if(data.threat !== undefined){
			txt += "Threat: "+(data.threat || 0)+"<br>"
		}
		return txt
	})
	t.add_class("command","full_btn")
	t.add_button("command","Attack",null,r=>send("start-battle",{"target":r.name}))
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
			div.innerHTML = "Dock(i)"
			div.onclick = ()=>{
				window.location.href = '/dock.html'+window.location.search
			}
		}
		if(other_ships[name].wormhole){
			div.innerHTML = "Jump(i)"
			div.onclick = ()=>{
				send("jump")
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
		var shipdef = msg.ship_defs[data.type]
		var stats = pships[data.name].stats
		var txt = ""
		txt += "Ship: "+shipdef.name+"<br>"
		txt += "Threat: "+data.threat+"<br>"
		txt += "Room: "+stats.room.current+"/"+stats.room.max+"<br>"
		return txt
	})
	t2.add_class("command","full_btn")
	t2.add_button("name",null,null,r=>{
		pship = pships[r.name]
		localStorage.setItem("ship",r.name)
		update_inventory()
		update_ships(msg)
	})
	t2.for_col("name",(div,r)=>{
		if(r.name === pship.name){
			var parent = div.parentNode
			var classes = div.classList
			var children = Array.from(div.childNodes)
			div.remove()
			var new_div = f.addElement(parent,"div",f.shipName(pship,"character"))
			new_div.classList.add(...classes)
			children.forEach(c=>{
				if(c.nodeName === "#text"){return}
				new_div.appendChild(c)
			})
		}
	})
	t2.add_button("command","guard",null,r=>send("guard",{"ship":r.name}))
	t2.update(own_following)
	
	var t3 = f.make_table(window.own_guards,"img","name","command")
	t3.format("name",e=>f.shipName(e,"character"))
	//t3.sort("name")
	t3.max_chars("name",24)
	t3.add_tooltip2("name",data=>{
		var shipdef = msg.ship_defs[data.type]
		var txt = ""
		txt += "Ship: "+shipdef.name+"<br>"
		txt += "Threat: "+data.threat+"<br>"
		txt += "Room: "+data.stats.room.current+"/"+data.stats.room.max+"<br>"
		return txt
	})
	t3.add_class("command","full_btn")
	t3.add_button("command","follow",null,r=>send("follow",{"ship":r.name}))
	t3.update(own_guarding)
}
var last_other_ship
var usable_items = []
function update_inventory(){
	window.ship_name.value = "Ship: " + f.shipName(pship,"character")
	var stats = cdata.stats
	var items = cdata.items
	var gear = pship.gear
	window.room.innerHTML = "Room left: "+func.formatNumber(stats.room.current)+"/"+func.formatNumber(stats.room.max)
	
	//gear tab
	//I wish headers were easier to define. The object syntax is a mess and unneeded.
	//Arrays would be better
	usable_items = []
	var t = f.make_table(window.inv_gear_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"})
	t.sort("name")
	t.add_tooltip("name")
	t.add_class("name","full_btn")
	t.max_chars("name",24)
	t.add_button("name",null,{"usable":true},r=>{
		console.log(r,r.name)
		send("use_item",{"item":r.name})
	})
	t.for_col("name",(div,r,name)=>{
		if(t.data[name].usable){
			usable_items.push(name)
			div.innerHTML += "("+String(usable_items.length)+")"
		}
	})
	t.update(f.join_inv(items,idata))
	
	var t2 = f.make_table(window.gear_list,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"})
	t2.sort("name")
	t2.add_tooltip("name")
	t2.add_class("name","full_btn")
	t2.max_chars("name",30)
	t2.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);send("use_item",{"item":r.name})})
	t2.for_col("name",(div,r,name)=>{
		if(t2.data[name].usable){
			if(!usable_items.includes(name)){usable_items.push(name)}
			div.innerHTML += "("+String(usable_items.indexOf(name)+1)+")"
		}
	})
	t2.update(f.join_inv(gear,idata))
	f.forClass("empty_inv",e=>{
		e.style = Object.keys(items).length ? "display:none" : "display:initial"
	})
	window.empty_gear.style = Object.keys(gear).length ? "display:none" : "display:initial"
	//loot tab
	var t3 = f.make_table(window.inv_loot_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t3.sort("name")
	t3.add_tooltip("name")
	t3.add_class("name","full_btn")
	t3.add_class("amount","mouseover_underline")
	t3.max_chars("name",24)
	t3.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);send("use_item",{"item":r.name})})
	t3.add_input("transfer","number",null,0)
	t3.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t3.for_col("name",(div,r,name)=>{
		if(t3.data[name].usable){
			div.innerHTML += "("+String(usable_items.indexOf(name)+1)+")"
		}
	})
	t3.update(f.join_inv(items,idata))
	
	var t4 = f.make_table(window.inv_loot_loot,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t4.sort("name")
	t4.add_tooltip("name")
	t4.add_class("amount","mouseover_underline")
	t4.max_chars("name",24)
	t4.add_input("transfer","number",null,0)
	t4.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		var room = pship.stats.room.current
		var max = Math.floor(room/idata[r.name].size)
		amount = Math.min(amount,max)
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t4.update(f.join_inv(tile.items||{},idata))
	window.empty_loot.style = Object.keys(tile.items||{}).length ? "display:none" : "display:initial"
	
	window.drop_all.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.drop.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.loot_all.style = Object.keys(tile.items||{}).length ? "display:initial" : "display:none"
	window.loot.style = Object.keys(tile.items||{}).length ? "display:initial" : "display:none"
	window.drop.onclick = ()=>do_drop(t3.get_input_values("transfer"))
	window.loot.onclick = ()=>do_loot(t4.get_input_values("transfer"))
	//trade tab
	var other_room_left
	var t5 = f.make_table(window.inv_trade_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t5.sort("name")
	t5.add_tooltip("name")
	t5.add_class("name","full_btn")
	t5.add_class("amount","mouseover_underline")
	t5.max_chars("name",24)
	t5.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);send("use_item",{"item":r.name})})
	t5.add_input("transfer","number",null,0)
	t5.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		var max = Math.floor(other_room_left/idata[r.name].size)
		amount = Math.min(amount,max)
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t5.for_col("name",(div,r,name)=>{
		if(t5.data[name].usable){
			div.innerHTML += "("+String(usable_items.indexOf(name)+1)+")"
		}
	})
	t5.update(f.join_inv(items,idata))
	
	window.other_name.innerHTML = ""
	Object.keys(tile.ships).forEach(owner=>{
		if(owner === cdata.name){return}
		var op = f.addElement(window.other_name,"option",owner)
		op.value = owner
	})
	window.give_credits_amount.value == ""
	window.other_name.onchange = e=>{
		var other_character = e.target.value
		other_cdata = characters[other_character]
		window.give_credits.onclick = ()=>{
			var target = other_character
			var amount = Math.floor(Number(window.give_credits_amount.value))
			send("give-credits-character",{target,amount})
		}
		var other_room = other_cdata.stats.room
		window.other_room.innerHTML = "Room left: "+String(other_cdata.stats.room.current)+"/"+String(other_cdata.stats.room.max)
		other_room_left = other_cdata.stats.room.current
	}
	window.other_name.value && window.other_name.onchange({target:{value:window.other_name.value}})
	window.give.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.give.onclick = ()=>{
		var table = {
			data: [
				{
					action: "give",
					self: cdata.name,
					other: window.other_name.value,
					items: t5.get_input_values("transfer")
				}
			]
		}
		send("ship-trade",table)
	}
}
function do_move(e){
	if(!nav.map){console.log("ignoring move, map not loaded yet");return}
	var cell = e.target
	if(cell.nodeName === "TABLE"){return}
	if(cell.nodeName === "IMG"){cell = cell.parentNode}
	var [x,y] = position
	var x2 = x+cell.coord_x
	var y2 = y+cell.coord_y
	if(cell.coord_x === 0 && cell.coord_y === 0){
		interact()
	}
	else{
		send("move",{"position":[x2,y2]})
	}
}
function interact(){
	if(tile.jump_target){
		do_jump()
	}
	else if(structure.name){
		window.location.href = '/dock.html'+window.location.search
	}
	else if(attack_target){
		do_attack()
	}
	else{
		do_gather()
	}
}
function do_attack(){
	send("start-battle",{"target":attack_target})
}
var do_gather = ()=>send("gather")
var do_excavate = ()=>send("excavate")
var do_investigate = ()=>send("investigate")
var do_loot_all = ()=>send("take-loot",{"ship":pship.name,"items":tile.items||{}})
var do_loot = (i)=>send("take-loot",{"ship":pship.name,"items":i})
var do_jump = ()=>send("jump",{"wormhole":tile.wormhole})
var do_pack = ()=>send("pack-station")
var do_dropall = ()=>send("drop",{"items":cdata.items})
var do_drop = (i)=>{send("drop",{"items":i});console.log(i)}
var do_hwr = ()=>send("homeworld-return")
var do_rename = ()=>{
	send("ship-rename",{"name":window.ship_name.value})
}

function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "flex";
  evt.currentTarget.className += " active";
}

var td_rules = []
var last_width
function resize(){
	var style = window.getComputedStyle(window.map_container)
	var left = parseFloat(style.marginLeft,1000)
	var right = parseFloat(style.marginRight,1000)
	var fill_ratio = 0.7
	var box_width = (window.map_container.offsetWidth+left+right)*fill_ratio
	var side_length = vision*2+1
	var min_container_width = 350/side_length
	var max_width = Math.max(window.innerHeight/side_length*fill_ratio,min_container_width)
	var width = Math.min(Math.max(min_container_width,box_width/side_length),max_width)
	if(!last_width || Math.abs(last_width-width) > 0.1){
		td_rules.forEach(r=>config.styles.deleteRule(r))
		td_rules = []
		td_rules.push(config.styles.insertRule("#space_map td{width:"+width+"px;height:"+width+"px;}"))
		window.info_display.style.width = width*side_length+"px"
		last_width = width
	}
	
}
window.addEventListener('resize',resize)

window.gather.onclick = do_gather
window.excavate.onclick = do_excavate
window.investigate.onclick = do_investigate
window.loot_all.onclick = do_loot_all
window.pack.onclick = do_pack
window.drop_all.onclick = do_dropall
window.hwr_btn.onclick = do_hwr
window.ship_name.onfocus = e=>{
	e.target.value = pship.custom_name || ""
	window.onkeydown = null
}
window.ship_name.onblur = do_rename
window.ship_name.onkeydown = e=>{
	if(e.code === "Enter"){
		e.target.blur()
	}
}
window.space_map.onclick = do_move
function keyboard_move(e){
	if(e.shiftKey || e.ctrlKey){return}
	if(e.repeat && (/*Date.now()-last_action_time < 100 || */move_delay_timer)){return}
	if(e.code === "Enter" && document.activeElement.nodeName === "INPUT"){
		e.target.blur()
		return
	}
	var name = document.activeElement.nodeName
	if(["INPUT","TEXTAREA"].includes(name)){return}
	var right=["KeyD","Numpad6","ArrowRight"].includes(e.code)
	var left=["KeyA","Numpad4","ArrowLeft"].includes(e.code)
	var up=["KeyW","Numpad8","ArrowUp"].includes(e.code)
	var down=["KeyS","Numpad2","ArrowDown"].includes(e.code)
	if(left){send("move-relative",{"position":[-1,0]})}
	else if(right){send("move-relative",{"position":[1,0]})}
	else if(up){send("move-relative",{"position":[0,1]})}
	else if(down){send("move-relative",{"position":[0,-1]})}
	else if(e.code==="KeyG"){do_gather()}
	else if(e.code==="KeyI"){interact()}
	else if(e.code==="KeyK"){do_attack()}
	else if(e.code==="KeyL"){do_loot_all()}
	else if(e.code==="KeyJ"){do_jump()}
	else if(e.code==="Enter"){interact()}
	else if(e.code==="Numpad5"){interact()}
	else if(e.code==="Space"){interact()}
	else if(e.code.includes("Digit")){
		var nr = Number(e.code.substring(5,6))
		if(nr <= usable_items.length){
			send("use_item",{"item":usable_items[nr-1]})
		}
	}
	// diagonals
	else if(e.code==="Numpad9"){send("move-relative",{"position":[ 1, 1]})}
	else if(e.code==="Numpad3"){send("move-relative",{"position":[ 1,-1]})}
	else if(e.code==="Numpad7"){send("move-relative",{"position":[-1, 1]})}
	else if(e.code==="Numpad1"){send("move-relative",{"position":[-1,-1]})}
	else{return}
	e.preventDefault()
}
var ready = f=>["complete","interactive"].includes(document.readyState) ? f() : document.addEventListener("DOMContentLoaded",f)

ready(()=>{
	if(!nav.map){console.log("nav.map not loaded early enough.")}
	send("get-location")
})
// right click
// var notepad = document.getElementById("notepad");
// notepad.addEventListener("contextmenu",function(event){
    // event.preventDefault();
    // var ctxMenu = document.getElementById("ctxMenu");
    // ctxMenu.style.display = "block";
    // ctxMenu.style.left = (event.pageX - 10)+"px";
    // ctxMenu.style.top = (event.pageY - 10)+"px";
// },false);
// notepad.addEventListener("click",function(event){
    // var ctxMenu = document.getElementById("ctxMenu");
    // ctxMenu.style.display = "";
    // ctxMenu.style.left = "";
    // ctxMenu.style.top = "";
// },false);
