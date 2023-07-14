config.apply()
var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var ship
var vision = 0
var pship
var pships
var cdata
var terrain = {}
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
			if(Object.keys(hwr).length){
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
				window.hwr_box.style.display = "initial"
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
			console.log(cdata)
			position = [x,y]
			if(msg.vision !== vision){
				nav.map.init(window.space_map,msg.vision)
			}
			vision = msg.vision
			nav.map.update(x,y,tiles)
			update_inventory()
			//buttons
			for(let [btn,display] of Object.entries(msg.buttons)){
				window[btn].style = "display:"+display
			}
			window.jump.style = tile.object ? "display:initial" : "display:none"
			window.pack.style = msg.structure?.owner === cdata.name ? "display:initial" : "display:none"
			//ship
			if(pship.img !== ship.src){
				ship.src = pship.img
			}
			ship.style = "transform: rotate("+String(rotation)+"deg);"
			//station
			if((Object.keys(msg.structure).length && msg.structure.image) || tile.img){
				ship.style.display = "none"
			}
			else{
				ship.style.display = "initial"
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
function update_starmap(msg){
	window.starmap.innerHTML = ""
	var sm = msg.starmap
	f.row(window.starmap,sm.nw||"",sm.n||"",sm.ne||"")
	f.row(window.starmap,sm.w||"",pship.pos.system,sm.e||"")
	f.row(window.starmap,sm.sw||"",sm.s||"",sm.se||"")
}
function update_ships(msg){
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
	window.empty_ships.style = stranger ? "display:none" : "display:initial"
	window.empty_follower.style = follower ? "display:none" : "display:initial"
	window.empty_guard.style = guarding ? "display:none" : "display:initial"
	stranger && f.headers(ships,"img","owner","trade","attack")
	follower && f.headers(own_ships,"img","name","command")
	guarding && f.headers(own_guards,"img","name","command")
	for(let tships of Object.values(msg.tile.ships)){
		tships.forEach(s=>{
			var active_ship_div
			// hot ships near you
			if(s.owner !== cdata.name){
				var row = f.addElement(ships,"tr")
				var td1 = f.addElement(row,"td")
				var img = f.addElement(td1,"img")
				img.setAttribute("src",s.img)
				img.title = s.type
				f.addElement(row,"td",f.shipName(s,"stranger"))
				var td2= f.addElement(row,"td")
				var btn_trade = f.addElement(td2,"button","trade")
				btn_trade.onclick = ()=>start_trade(s)
				var td3= f.addElement(row,"td")
				var btn_attack = f.addElement(td3,"button","attack")
				btn_attack.onclick = ()=>{
					send("start-battle",{"target":s.name})
				}
			}
			else{
				if(cdata.ships.includes(s.name)){
					// following
					var row = f.addElement(own_ships,"tr")
					var td1 = f.addElement(row,"td")
					var img = f.addElement(td1,"img")
					img.setAttribute("src",s.img)
					img.title = s.type
					var btn_box = f.addElement(row,"td")
					btn_box.setAttribute("class","active_ship "+s.name)
					var btn = f.addElement(btn_box,"button",f.shipName(s,"test"))
					btn.title = "click to select"
					var btn_active=f.addElement(btn_box,"label",f.shipName(s,"test"))
					btn_active.style.display="none"
					btn.style.display="initial"
					btn.onclick = ()=>{
						pship = pships[s.name]
						localStorage.setItem("ship",s.name)
						update_inventory()
						update_ships(msg)
					}
					if(pship.name===s.name){
						btn_active.style.display="initial"
						btn.style.display="none"
					}
					var btn_box2 = f.addElement(row,"td")
					var btn2 = f.addElement(btn_box2,"button","guard")
					btn2.onclick = ()=>{
						send("guard",{"ship":s.name})
					}
				}
				else{
					// guarding
					var row = f.addElement(own_guards,"tr")
					var td1 = f.addElement(row,"td")
					var img = f.addElement(td1,"img")
					img.setAttribute("src",s.img)
					img.title = s.type
					f.addElement(row,"td",f.shipName(s,"test"))
					var btn_box = f.addElement(row,"td")
					var btn = f.addElement(btn_box,"button","follow")
					btn.onclick = ()=>{
						send("follow",{"ship":s.name})
					}
				}
			}
		})
	}
}
function update_inventory(){
	window.ship_name.value = "Ship: " + f.shipName(pship,"character")
	var ship_inv = pship.inventory
	var items = ship_inv.items
	var gear = ship_inv.gear
	if(ship_inv.space_extra){
		window.space.innerHTML = "Space left: "+func.formatNumber(ship_inv.space_left)+"/"+func.formatNumber((ship_inv.space_max+ship_inv.space_extra))
	}
	else{
		window.space.innerHTML = "Space left: "+func.formatNumber(ship_inv.space_left)+"/"+func.formatNumber(ship_inv.space_max)
	}
	var t = f.make_table(window.inventory,"img",{"name":"item"},{"amount":"#"},"size","action")
	t.add_tooltip("name")
	t.add_button("action","use",{"usable":true},r=>{console.log(r,r.name);send("use_item",{"item":r.name})})
	t.update(f.join_inv(pship.inventory.items,idata))
	
	var t = f.make_table(window.gear_list,"img",{"name":"item"},{"amount":"#"},"size")
	t.add_tooltip("name")
	t.update(f.join_inv(pship.inventory.gear,idata))
	window.empty_inv.style = Object.keys(items).length ? "display:none" : "display:initial"
	window.empty_gear.style = Object.keys(gear).length ? "display:none" : "display:initial"
	window.drop_all.style = Object.keys(items).length ? "display:initial" : "display:none"
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
function do_move(e){
	if(!nav.map){console.log("ignoring move, map not loaded yet");return}
	var cell = e.target
	if(cell.nodeName === "TABLE"){return}
	if(cell.nodeName === "IMG"){cell = cell.parentNode}
	var [x,y] = position
	var x2 = x+cell.coord_x
	var y2 = y+cell.coord_y
	if(cell.coord_x === 0 && cell.coord_y === 0){
		if(tile.jump_target){
			do_jump()
		}
		else if(structure.name){
			window.location.href = '/trade.html'+window.location.search
		}
	}
	else{
		send("move",{"position":[x2,y2]})
	}
}
var do_gather = ()=>send("gather")
var do_excavate = ()=>send("excavate")
var do_investigate = ()=>send("investigate")
var do_loot = ()=>send("take-loot",{"ship":pship.name,"items":tile.items})
var do_jump = ()=>send("jump",{"wormhole":tile.object})
var do_pack = ()=>send("pack-station")
var do_dropall = ()=>send("drop",{"items":pship.inventory.items})
var do_hwr = ()=>send("homeworld-return")
var do_rename = ()=>send("ship-rename",{"name":window.ship_name.value})

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
function resize(){
	var style = window.getComputedStyle(window.map_container)
	var left = parseInt(style.marginLeft,10)
	var right = parseInt(style.marginRight,10)
	var fill_ratio = 0.7
	var box_width = (window.map_container.offsetWidth+left+right)*fill_ratio
	var side_length = vision*2+1
	var max_width = Math.max(window.innerHeight/side_length*fill_ratio,50)
	var width = Math.min(Math.max(50,box_width/side_length),max_width)
	td_rules.forEach(r=>config.styles.deleteRule(r))
	td_rules = []
	td_rules.push(config.styles.insertRule("#space_map td{width:"+width+"px;height:"+width+"px;}"))
}
resize()
window.addEventListener('resize',resize)

window.gather.onclick = do_gather
window.excavate.onclick = do_excavate
window.investigate.onclick = do_investigate
window.loot.onclick = do_loot
window.jump.onclick = do_jump
window.pack.onclick = do_pack
window.drop_all.onclick = do_dropall
window.hwr_btn.onclick = do_hwr
window.transfer_items_close.onclick = ()=>window.transfer_items_modal.style.display = "none"
window.transfer_items_btn.onclick = do_trade
window.ship_name.onfocus = e=>e.target.value = pship.custom_name || pship.type+" "+pship.id
window.ship_name.onblur = do_rename
window.space_map.onclick = do_move

var ready = (f)=>{document.readyState === "complete" ? f() : document.addEventListener("DOMContentLoaded",f)}

ready(()=>{
	if(!nav.map){console.log("nav.map not loaded early enough.")}
	send("get-location")
})