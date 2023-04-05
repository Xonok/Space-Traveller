var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var map = window.space_map
var grid = {}
function init_map(vision){
	map.innerHTML = ""
	var tiles_x = 1+vision*2
	var tiles_y = 1+vision*2
	var x_min = Math.floor(-(tiles_x-1)/2)
	var x_max = Math.floor((tiles_x+1)/2)
	var y_min = Math.floor(-(tiles_y-1)/2)
	var y_max = Math.floor((tiles_y+1)/2)
	grid = {}
	for(let y = y_min;y<y_max;y++){
		var row = f.addElement(map,"tr")
		for(let x = x_min;x<x_max;x++){
			if(!grid[x]){grid[x]={}}
			var cell = f.addElement(row,"td")
			cell.coord_x = x
			cell.coord_y = y
			grid[x][y] = cell
		}
	}
	if(!ship){
		ship = f.addElement(grid[0][0],"img")
	}
}

var ship
var vision
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
			if(Object.keys(hwr).length){
				window.hwr_name.innerHTML = hwr.name
				window.hwr_charges.innerHTML = "Charges: "+hwr.charges+"/"+hwr.max_charges
				if(hwr.charges){
					window.hwr_status.innerHTML = "Status: "+hwr.time_left
				}
				else{
					window.hwr_status.innerHTML = "Status: ready in "+hwr.time_left
				}
				window.hwr_box.style.display = "initial"
			}
			else{
				window.hwr_box.style.display = "none"
			}
			var tiles = msg.tiles
			var {x,y,rotation} = pship.pos
			window.credit.innerHTML= "Credits: "+func.formatNumber(cdata.credits)
			window.constellation.innerHTML="Constellation: " + msg.constellation
			window.place.innerHTML="System: "+ pship.pos.system
			window.player_position.innerHTML="Coordinates: "+pship.pos.x+","+pship.pos.y
			window.tile_terrain.innerHTML = "Terrain: "+msg.tile.terrain
			if(msg.tile.resource){
				window.tile_resource.innerHTML = "Resource: "+msg.tile.resource+"("+msg.tile.resource_amount+")"
			}
			else{
				window.tile_resource.innerHTML = "Resource: none"
			}
			update_ships(msg)
			console.log(cdata)
			position = [x,y]
			if(msg.vision !== vision){
				init_map(msg.vision)
			}
			vision = msg.vision
			for(let [x2,row] of Object.entries(tiles)){
				for(let [y2,tile] of Object.entries(row)){
					var x3 = x2-x
					var y3 = y2-y
					if(!grid[x3]?.[y3]){continue}
					var cell = grid[x3][y3]
					color = terrain_color[tile.terrain]
					cell.style.backgroundColor = color
					cell.style.color = invertColour(color || "#0000FF")
					if(tile.variation){
						cell.style.backgroundImage = "url(/img/tiles/"+terrain_color_name[tile.terrain]+"/"+tile.variation+".png)"
					}
					else{
						cell.style.backgroundImage = null
					}
					Array.from(cell.childNodes).forEach(n=>{
						if(n.object || n.structure || n.ship){
							n.remove()
						}
					})
					if(tile.structure){
						var structure_img = f.addElement(cell,"img")
						structure_img.src = tile.structure.image
						structure_img.structure = true
					}
					if(tile.img){
						var tile_img = f.addElement(cell,"img")
						tile_img.src = tile.img
						tile_img.object = true
					}
					if(!tile.structure && !tile.img && tile.ship && (x3 != 0 || y3 != 0)){
						var ship_img = f.addElement(cell,"img")
						ship_img.src = tile.ship.img
						ship_img.style = "transform: rotate("+String(tile.ship.rotation)+"deg);"
						ship_img.ship = true
					}
				}
			}
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
	stranger && f.headers(ships,"img","owner","ship type","trade","attack")
	follower && f.headers(own_ships,"name","status","command")
	guarding && f.headers(own_guards,"name","command")
	for(let tships of Object.values(msg.tile.ships)){
		tships.forEach(s=>{
			var active_ship_div
			// hot ships near you
			if(s.owner !== cdata.name){
				var row = f.addElement(ships,"tr")
				var td1 = f.addElement(row,"td")
				var img = f.addElement(td1,"img")
				img.setAttribute("src",s.img)
				f.addElement(row,"td",s.owner)
				f.addElement(row,"td",s.type)
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
					f.addElement(row,"td",s.custom_name || s.type+" "+s.id)
					var btn_box = f.addElement(row,"td")
					btn_box.setAttribute("class","active_ship "+s.name)
					var btn = f.addElement(btn_box,"button","select")
					var btn_active=f.addElement(btn_box,"label","active")
					btn_active.style.display="none"
					btn.style.display="initial"
					btn.onclick = ()=>{
						pship = pships[s.name]
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
					f.addElement(row,"td",s.custom_name || s.name)
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
	var name = window.ship_name
	window.ship_name.value = "Ship: " + (pship.custom_name || pship.type+" "+pship.id)
	var ship_inv = pship.inventory
	var items = ship_inv.items
	var gear = ship_inv.gear
	if(ship_inv.space_extra){
		window.space.innerHTML = "Space left: "+func.formatNumber(ship_inv.space_left)+"/"+func.formatNumber((ship_inv.space_max+ship_inv.space_extra))
	}
	else{
		window.space.innerHTML = "Space left: "+func.formatNumber(ship_inv.space_left)+"/"+func.formatNumber(ship_inv.space_max)
	}
	var inv = window.inventory
	inv.innerHTML = ""
	if(Object.values(items).length){
		f.headers(inv,"","item","amount","action")
	}
	for(let [item,amount] of Object.entries(items)){
		let tr = f.addElement(inv,"tr")
		var imgbox = f.addElement(tr,"td")
		f.addElement(imgbox,"img").src = idata[item].img
		var item_name = f.addElement(tr,"td",idata[item].name)
		item_name.setAttribute("class","item_name "+name)
		f.tooltip(item_name,idata[item])
		f.addElement(tr,"td",String(amount))
		var button_cell=f.addElement(tr,"td")
		if(idata[item].usable){
			var btn = f.addElement(button_cell,"button","use")
			btn.onclick = ()=>{send("use_item",{"item":item})}
		}
	}
	var glist = window.gear_list
	glist.innerHTML = ""
	if(Object.values(gear).length){
		f.headers(glist,"","item","amount")
	}
	for(let [item,amount] of Object.entries(gear)){
		let tr = f.addElement(glist,"tr")
		var imgbox = f.addElement(tr,"td")
		f.addElement(imgbox,"img").src = idata[item].img
		var item_name = f.addElement(tr,"td",idata[item].name)
		item_name.setAttribute("class","item_name "+name)
		f.tooltip(item_name,idata[item])
		f.addElement(tr,"td",String(amount))
	}
	window.empty_inv.style = Object.keys(items).length ? "display:none" : "display:initial"
	window.empty_gear.style = Object.keys(gear).length ? "display:none" : "display:initial"
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
	//send("ship-trade",{"target":s.name,"items":pship.inventory.items})
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
	send("ship-trade",{"target":window.transfer_items.target,"items":table})
	window.transfer_items.innerHTML = ""
	window.transfer_items_modal.style.display = "none"
}
function do_move(e){
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

send("get-location")

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
window.map.onclick = do_move
