const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}
window.gather.onclick = do_gather
window.loot.onclick = do_loot
window.jump.onclick = do_jump
window.drop_all.onclick = do_dropall
window.hwr_btn.onclick = do_hwr
var map = window.space_map
map.onclick = do_move
var grid = {}

var tiles_x = 7
var tiles_y = 7
var x_min = Math.floor(-(tiles_x-1)/2)
var x_max = Math.floor((tiles_x+1)/2)
var y_min = Math.floor(-(tiles_y-1)/2)
var y_max = Math.floor((tiles_y+1)/2)
var grid = {}
for(let y = y_min;y<y_max;y++){
	var row = addElement(map,"tr")
	for(let x = x_min;x<x_max;x++){
		if(!grid[x]){grid[x]={}}
		var cell = addElement(row,"td")
		cell.coord_x = x
		cell.coord_y = y
		grid[x][y] = cell
	}
}

var pship
var terrain = {}
var position = [0,0]
var idata = {}
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
			Array.from(document.getElementsByTagName("td")).forEach(e=>{
				e.style.backgroundColor = null
				if(e.coord_x !== 0 || e.coord_y !== 0){
					e.innerHTML = ""
				}
			})
			var msg = JSON.parse(e.target.response)
			console.log(msg)
			var pdata = msg.pdata
			pship = msg.ships[pdata.ship]
			var pships = msg.ships
			idata = msg["idata"]
			tile = msg["tile"]
			hwr = msg["hwr"]
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
			window.credit.innerHTML= "Credits: "+pdata.credits
			window.constellation.innerHTML="You are in constellation " + msg.constellation + "."
			window.place.innerHTML="You are in "+ pship.pos.system+"."
			window.player_position.innerHTML="Your coordinates are X:"+pship.pos.x+", Y: "+pship.pos.y
			window.tile_terrain.innerHTML = "Terrain: "+msg.tile.terrain
			if(msg.tile.resource){
				window.tile_resource.innerHTML = "Resource: "+msg.tile.resource+"("+msg.tile.resource_amount+")"
			}
			else{
				window.tile_resource.innerHTML = "Resource: none"
			}
			var ships = window.ships
			var own_ships = window.own_ships
			var own_guards = window.own_guards
			ships.innerHTML=""
			own_ships.innerHTML = ""
			own_guards.innerHTML = ""
			var ship_names=Object.values(msg.tile.ships)
			var stranger = ship_names.find(p=>p.find(s=>s.owner !== pdata.name))
			var follower = ship_names.find(p=>p.find(s=>pdata.ships.includes(s.name)))
			var guarding = ship_names.find(p=>p.find(s=>!pdata.ships.includes(s.name)))
			window.empty_ships.style = stranger ? "display:none" : "display:initial"
			window.empty_follower.style = follower ? "display:none" : "display:initial"
			window.empty_guard.style = guarding ? "display:none" : "display:initial"
			stranger && headers(ships,"img","owner","ship type","trade","attack")
			follower && headers(own_ships,"name","status","command")
			guarding && headers(own_guards,"name","command")
			for(let tships of Object.values(msg.tile.ships)){
				tships.forEach(s=>{
					if(s.owner !== pdata.name){
						var row = addElement(ships,"tr")
						var td1 = addElement(row,"td")
						var img = addElement(td1,"img")
						img.setAttribute("src",s.img)
						addElement(row,"td",s.owner)
						addElement(row,"td",s.type)
						var td2= addElement(row,"td")
						var btn_trade = addElement(td2,"button","trade")
						btn_trade.onclick = ()=>{
							send("ship-trade",{"target":s.name,"items":pship.inventory.items})
						}
						var td3= addElement(row,"td")
						var btn_attack = addElement(td3,"button","attack")
						btn_attack.onclick = ()=>{
							send("start-battle",{"target":s.name})
						}
					}
					else{
						if(pdata.ships.includes(s.name)){
							var row = addElement(own_ships,"tr")
							addElement(row,"td",s.name)
							var btn_box = addElement(row,"td")
							var btn = addElement(btn_box,"button","select")
							btn.onclick = ()=>{
								pship = pships[s.name]
								update_inventory()
							}
							var btn_box2 = addElement(row,"td")
							var btn2 = addElement(btn_box2,"button","guard")
							btn2.onclick = ()=>{
								send("guard",{"ship":s.name})
							}
						}
						else{
							var row = addElement(own_guards,"tr")
							addElement(row,"td",s.name)
							var btn_box = addElement(row,"td")
							var btn = addElement(btn_box,"button","follow")
							btn.onclick = ()=>{
								send("follow",{"ship":s.name})
							}
						}
					}
				})
			}
			console.log(pdata)
			position = [x,y]
			for(let [x2,row] of Object.entries(tiles)){
				for(let [y2,tile] of Object.entries(row)){
					var x3 = x2-x
					var y3 = y2-y
					if(!grid[x3]?.[y3]){continue}
					var cell = grid[x3][y3]
					color = terrain_color[tile.terrain]
					cell.style.backgroundColor = color
					cell.style.color = invertColour(color || "#0000FF")
					Array.from(cell.childNodes).forEach(n=>{
						if(n.object || n.structure || n.ship){
							n.remove()
						}
					})
					if(tile.structure){
						var structure_img = addElement(cell,"img")
						structure_img.src = tile.structure.image
						structure_img.structure = true
					}
					if(tile.img){
						var tile_img = addElement(cell,"img")
						tile_img.src = tile.img
						tile_img.object = true
					}
					if(!tile.structure && !tile.img && tile.ship && (x3 != 0 || y3 != 0)){
						var ship_img = addElement(cell,"img")
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

function update_inventory(){
	var inv = pship.inventory
	var items = inv.items
	var gear = inv.gear
	window.space.innerHTML = "Space left: "+inv.space_left+"/"+inv.space_max
	var inv = window.inventory
	inv.innerHTML = ""
	if(Object.values(items).length){
		headers(inv,"","item","amount","action")
	}
	for(let [item,amount] of Object.entries(items)){
		let tr = addElement(inv,"tr")
		var imgbox = addElement(tr,"td")
		addElement(imgbox,"img").src = idata[item].img
		addElement(tr,"td",idata[item].name)
		addElement(tr,"td",String(amount))
		var button_cell=addElement(tr,"td")
		if(idata[item].usable){
			var btn = addElement(button_cell,"button","use")
			btn.onclick = ()=>{send("use_item",{"item":item})}
		}
	}
	var glist = window.gear_list
	glist.innerHTML = ""
	if(Object.values(gear).length){
		headers(glist,"","item","amount")
	}
	for(let [item,amount] of Object.entries(gear)){
		let tr = addElement(glist,"tr")
		var imgbox = addElement(tr,"td")
		addElement(imgbox,"img").src = idata[item].img
		addElement(tr,"td",idata[item].name)
		addElement(tr,"td",String(amount))
	}
	window.empty_inv.style = Object.keys(items).length ? "display:none" : "display:initial"
	window.empty_gear.style = Object.keys(gear).length ? "display:none" : "display:initial"
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

function do_move(e){
	var cell = e.target
	if(cell.nodeName === "TABLE"){return}
	if(cell.nodeName === "IMG"){cell = cell.parentNode}
	var [x,y] = position
	var x2 = x+cell.coord_x
	var y2 = y+cell.coord_y
	send("move",{"position":[x2,y2]})
}
function do_gather(){
	send("gather")
}
function do_loot(){
	send("take-loot",{"ship":pship.name,"items":tile.items})
}
function do_jump(){
	send("jump",{"wormhole":tile.object})
}
function do_dropall(){
	send("drop",{"items":items})
}
function do_hwr(){
	send("homeworld-return")
}

send("get-location")

var ship = addElement(grid[0][0],"img")

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