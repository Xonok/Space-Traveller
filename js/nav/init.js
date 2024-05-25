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

function send(command,table={}){
	table.key = key
	table.command = command
	if(pship && !table.ship){
		table.ship = pship.name
	}
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
			window.onkeydown = keyboard_move
			window.error_display.innerHTML = ""
			window.info_display.innerHTML = ""
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
			if(local_ship && Object.keys(pships).includes(local_ship)){
				pship = msg.ships[local_ship]
			}
			idata = msg["idata"]
			structure = msg["structure"]
			tile = msg["tile"]
			hwr = msg["hwr"]
			msg.messages.forEach((m,mID)=>{
				window.info_display.innerHTML += m
				if(mID+1 < msg.messages.length){
					window.info_display.innerHTML += "<br>"
				}
			})
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
				window.hwr_name.innerHTML = "Homeworld Return Device<br>Ship: "+worst.name
				window.hwr_charges.innerHTML = "Charges: "+worst.charges+"/"+worst.max_charges
				if(worst.charges){
					window.hwr_status.innerHTML = "Status: "+worst.time_left
				}
				else{
					window.hwr_status.innerHTML = "Status: ready in "+worst.time_left
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
				window.tile_resource_text.innerHTML = noun_resource+msg.tile.resource+"("+msg.tile.resource_amount+")"
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
			resize()
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
	t.add_class("command","full_btn")
	t.add_button("command","Attack",null,r=>send("start-battle",{"target":r.name}))
	attack_target = null
	t.for_col("command",(div,r,name)=>{
		if(!other_ships[name].player){
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
				send("jump",{"wormhole":tile.wormhole})
			}
		}
		if(other_ships[name].player){
			div.remove()
		}
	})
	t.update(other_ships)
	
	var t2 = f.make_table(window.own_ships,"img","name","command")
	t2.format("name",e=>f.shipName(e,"character"))
	t2.sort("name")
	t2.max_chars("name",24)
	t2.add_class("name","full_btn")
	t2.add_class("command","full_btn")
	t2.add_button("name",null,null,r=>{
		pship = pships[r.name]
		localStorage.setItem("ship",r.name)
		update_inventory()
		update_ships(msg)
	})
	t2.for_col("name",(div,r)=>{
		if(r.name === pship.name){
			div.parentNode.innerHTML = f.shipName(pship,"character")
		}
	})
	t2.add_button("command","guard",null,r=>send("guard",{"ship":r.name}))
	t2.update(own_following)
	
	var t3 = f.make_table(window.own_guards,"img","name","command")
	t3.format("name",e=>f.shipName(e,"character"))
	t3.sort("name")
	t3.max_chars("name",24)
	t3.add_class("command","full_btn")
	t3.add_button("command","follow",null,r=>send("follow",{"ship":r.name}))
	t3.update(own_guarding)
}
var last_other_ship
var usable_items = []
function update_inventory(){
	window.ship_name.value = "Ship: " + f.shipName(pship,"character")
	var ship_inv = pship.inventory
	var items = ship_inv.items
	var gear = ship_inv.gear
	if(ship_inv.room_extra){
		window.room.innerHTML = "Room left: "+func.formatNumber(ship_inv.room_left)+"/"+func.formatNumber((ship_inv.room_max+ship_inv.room_extra))
	}
	else{
		window.room.innerHTML = "Room left: "+func.formatNumber(ship_inv.room_left)+"/"+func.formatNumber(ship_inv.room_max)
	}
	
	//gear tab
	//I wish headers were easier to define. The object syntax is a mess and unneeded.
	//Arrays would be better
	usable_items = []
	var t = f.make_table(window.inv_gear_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"})
	t.sort("name")
	t.add_tooltip("name")
	t.add_class("name","dotted")
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
	t.update(f.join_inv(pship.inventory.items,idata))
	
	var t2 = f.make_table(window.gear_list,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"})
	t2.sort("name")
	t2.add_tooltip("name")
	t2.add_class("name","dotted")
	t2.add_class("name","full_btn")
	t2.max_chars("name",30)
	t2.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);send("use_item",{"item":r.name})})
	t2.update(f.join_inv(pship.inventory.gear,idata))
	f.forClass("empty_inv",e=>{
		e.style = Object.keys(items).length ? "display:none" : "display:initial"
	})
	window.empty_gear.style = Object.keys(gear).length ? "display:none" : "display:initial"
	//loot tab
	var t3 = f.make_table(window.inv_loot_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t3.sort("name")
	t3.add_tooltip("name")
	t3.add_class("name","dotted")
	t3.add_class("name","full_btn")
	t3.max_chars("name",24)
	t3.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);send("use_item",{"item":r.name})})
	t3.add_input("transfer","number",r=>{})
	t3.update(f.join_inv(pship.inventory.items,idata))
	
	var t4 = f.make_table(window.inv_loot_loot,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t4.sort("name")
	t4.add_tooltip("name")
	t4.add_class("name","dotted")
	t4.max_chars("name",24)
	t4.add_input("transfer","number",r=>{})
	t4.update(f.join_inv(tile.items||{},idata))
	window.empty_loot.style = Object.keys(tile.items||{}).length ? "display:none" : "display:initial"
	
	window.drop_all.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.drop.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.loot_all.style = Object.keys(tile.items||{}).length ? "display:initial" : "display:none"
	window.loot.style = Object.keys(tile.items||{}).length ? "display:initial" : "display:none"
	window.drop.onclick = ()=>do_drop(t3.get_input_values("transfer"))
	window.loot.onclick = ()=>do_loot(t4.get_input_values("transfer"))
	//trade tab
	var t5 = f.make_table(window.inv_trade_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t5.sort("name")
	t5.add_tooltip("name")
	t5.add_class("name","dotted")
	t5.add_class("name","full_btn")
	t5.max_chars("name",24)
	t5.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);send("use_item",{"item":r.name})})
	t5.add_input("transfer","number",r=>{})
	t5.update(f.join_inv(pship.inventory.items,idata))
	
	window.other_name.innerHTML = ""
	var ogroup = f.addElement(window.other_name,"optgroup")
	ogroup.label = cdata.name
	Object.keys(pships).filter(n=>n!==pship.name).forEach(n=>{
		var op = f.addElement(ogroup,"option",f.shipName(pships[n],"character"))
		op.value = n
	})
	var ship_to_owner = {}
	Object.entries(tile.ships).forEach(e=>{
		var owner = e[0]
		var tships = e[1]
		if(owner === cdata.name){return}
		if(!tships[0].player){return}
		var ogroup = f.addElement(window.other_name,"optgroup")
		ogroup.label = owner
		tships.forEach(tship=>{
			var op = f.addElement(ogroup,"option",f.shipName(tship,"character"))
			op.value = tship.name
			ship_to_owner[tship.name] = owner
		})
	})
	var t6
	window.other_name.onchange = e=>{
		var other_ship = e.target.value
		var other_pship = pships[other_ship]
		last_other_ship = other_ship
		if(!other_pship){
			window.inv_trade_other.innerHTML = ""
			window.take.style = "display:none"
			window.give_credits.style = "display:initial"
			window.give_credits_amount.style = "display:initial"
			window.give_credits_label.style = "display:initial"
			window.give_credits.onclick = ()=>{
				var target = ship_to_owner[other_ship]
				var amount = Math.floor(Number(window.give_credits_amount.value))
				send("give-credits-character",{target,amount})
			}
			return
		}
		window.give_credits.style = "display:none"
		window.give_credits_amount.style = "display:none"
		window.give_credits_label.style = "display:none"
		window.give_credits.onclick = null
		t6 = f.make_table(window.inv_trade_other,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
		t6.sort("name")
		t6.add_tooltip("name")
		t6.add_class("name","dotted")
		t6.max_chars("name",24)
		t6.add_input("transfer","number",r=>{})
		t6.update(f.join_inv(other_pship.inventory.items,idata))
		window.empty_other.style = Object.keys(other_pship.inventory.items||{}).length ? "display:none" : "display:initial"
		window.take.style = Object.keys(other_pship.inventory.items||{}).length ? "display:initial" : "display:none"
	}
	if(last_other_ship === pship.name){
		last_other_ship = null
	}
	window.other_name.value = last_other_ship || Object.keys(pships).filter(n=>n!==pship.name)[0]
	window.other_name.onchange({target:window.other_name})
	window.give.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.give.onclick = ()=>{
		var self = pship.name
		var other = window.other_name.value
		var items = t5.get_input_values("transfer")
		var table = {
			data: [
				{
					action: "give",
					self,
					other,
					sgear: false,
					ogear: false,
					items
				}
			]
		}
		send("ship-trade",table)
	}
	window.take.onclick = ()=>{
		var self = pship.name
		var other = window.other_name.value
		var items = t6.get_input_values("transfer")
		var table = {
			data: [
				{
					action: "take",
					self,
					other,
					sgear: false,
					ogear: false,
					items
				}
			]
		}
		send("ship-trade",table)
	}
}
function start_trade(target){
	window.transfer_items_modal.style.display = "block"
	f.headers(window.transfer_items,"item","amount")
	window.transfer_items.target = target.name
	Object.entries(pship.inventory.items).forEach(i=>{
		var item = i[0]
		var amount = i[1]
		var r = f.row(window.transfer_items,idata[item].name,f.input(0,f.only_numbers))
		r.item = item
	})
}
function do_trade(){
	var table = {}
	window.transfer_items.childNodes.forEach(r=>{
		if(r.type === "headers"){return}
		var item = r.item
		var amount = Number(r.childNodes[1].childNodes[0].value)
		if(amount){
			table[item] = amount
		}
	})
	var table2 = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: window.transfer_items.target,
				sgear: false,
				ogear: false,
				items: table
			}
		]
	}
	send("ship-trade",table2)
	window.transfer_items.innerHTML = ""
	window.transfer_items_modal.style.display = "none"
}
function do_trade_cancel(){
	window.transfer_items.innerHTML = ""
	window.transfer_items_modal.style.display = "none"
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
var do_loot_all = ()=>send("take-loot",{"ship":pship.name,"items":tile.items})
var do_loot = (i)=>send("take-loot",{"ship":pship.name,"items":i})
var do_jump = ()=>send("jump",{"wormhole":tile.wormhole})
var do_pack = ()=>send("pack-station")
var do_dropall = ()=>send("drop",{"items":pship.inventory.items})
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
	e.target.value = pship.custom_name || pship.type+" "+pship.id
	window.onkeydown = null
}
window.ship_name.onblur = do_rename
window.space_map.onclick = do_move
function keyboard_move(e){
	if(e.repeat){return}
	if(document.activeElement.nodeName === "INPUT"){return}
	var [x,y] = position
	var right=["KeyD","Numpad6","ArrowRight"].includes(e.code)
	var left=["KeyA","Numpad4","ArrowLeft"].includes(e.code)
	var up=["KeyW","Numpad8","ArrowUp"].includes(e.code)
	var down=["KeyS","Numpad2","ArrowDown"].includes(e.code)
	if(left){send("move",{"position":[x-1,y]})}
	else if(right){send("move",{"position":[x+1,y]})}
	else if(up){send("move",{"position":[x,y+1]})}
	else if(down){send("move",{"position":[x,y-1]})}
	else if(e.code==="KeyG"){do_gather()}
	else if(e.code==="KeyI"){interact()}
	else if(e.code==="KeyK")(do_attack())
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
	else if(e.code==="Numpad9"){send("move",{"position":[x+1,y+1]})}
	else if(e.code==="Numpad3"){send("move",{"position":[x+1,y-1]})}
	else if(e.code==="Numpad7"){send("move",{"position":[x-1,y+1]})}
	else if(e.code==="Numpad1"){send("move",{"position":[x-1,y-1]})}
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
