const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}
window.dock.onclick = ()=>window.location.href = "/trade.html"+window.location.search
window.quests.onclick = ()=>window.location.href = "/quests.html"+window.location.search
window.editor.onclick = ()=>window.location.href = "/editor.html"+window.location.search
window.forum.onclick = ()=>window.location.href = "/forum.html"+window.location.search
window.chat.onclick = ()=>window.location.href = "/chat.html"+window.location.search
window.gather.onclick = do_gather
window.drop_all.onclick = do_dropall
var map = window.space_map
map.onclick = do_move
var grid = {}

var tiles_x = 11
var tiles_y = 11
var x_min = Math.floor(-(tiles_x-1)/2)
var x_max = Math.floor((tiles_x+1)/2)
var y_min = Math.floor(-(tiles_y-1)/2)
var y_max = Math.floor((tiles_y+1)/2)
var grid = {}
for(let y = y_min;y<y_max;y++){
	var row = document.createElement("tr")
	for(let x = x_min;x<x_max;x++){
		if(!grid[x]){grid[x]={}}
		var cell = document.createElement("td")
		cell.coord_x = x
		cell.coord_y = y
		row.append(cell)
		grid[x][y] = cell
	}
	map.append(row)
}

var terrain = {}
var position = [0,0]
var items = {}
var terrain_color = {
	"energy":"#00bfff",
	"space":"#000000",
	"nebula":"#ff0000",
	"asteroids":"#808080",
	"exotic":"#7cfc00",
}

function createElement(type,inner){
	var e = document.createElement(type)
	if(inner){e.innerHTML = inner}
	return e
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

function send(table){
	table.key = key
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
			Array.from(document.getElementsByTagName("td")).forEach(e=>{
				e.style.backgroundColor = null
				if(e.coord_x !== 0 || e.coord_y !== 0){
					e.innerHTML = ""
				}
			})
			var msg = JSON.parse(e.target.response)
			console.log(msg)
			var pdata = msg["pdata"]
			var inv = pdata.inventory
			items = inv.items
			gear = inv.gear
			var tiles = msg.tiles
			var {x,y,rotation} = pdata.pos
			window.space.innerHTML = "Space: "+inv.space_left+"/"+inv.space_max
			position = [x,y]
			for(let [x2,row] of Object.entries(tiles)){
				for(let [y2,tile] of Object.entries(row)){
					var x3 = x2-x
					var y3 = y2-y
					if(!grid[x3]?.[y3]){continue}
					color = terrain_color[tile.terrain]
					grid[x3][y3].style.backgroundColor = color
					grid[x3][y3].style.color = invertColour(color || "#0000FF")
					Array.from(grid[x3][y3].childNodes).forEach(n=>{
						if(n.structure){
							n.remove()
						}
					})
					if(tile.structure){
						var structure_img = document.createElement("img")
						structure_img.src = tile.structure.image
						structure_img.structure = true
						grid[x3][y3].appendChild(structure_img)
					}
				}
			}
			//inventory
			var inv = window.inventory
			inv.innerHTML = ""
			while(inv.firstChild){
				inv.removeChild(inv.firstChild)
			}
			for(let [item,amount] of Object.entries(items)){
				let tr = document.createElement("tr")
				tr.append(createElement("td",item))
				tr.append(createElement("td",String(amount)))
				var btn = createElement("button","use")
				btn.onclick = ()=>{send({"command":"use_item","item":item})}
				tr.append(btn)
				inv.append(tr)
			}
			var glist = window.gear_list
			glist.innerHTML = ""
			for(let [item,amount] of Object.entries(gear)){
				let tr = document.createElement("tr")
				tr.append(createElement("td",item))
				tr.append(createElement("td",String(amount)))
				glist.append(tr)
			}
			if(Object.keys(items).length){
				window.empty_inv.style = "display:none";
			}
			else{
				window.empty_inv.style = "display:initial";
			}
			if(Object.keys(gear).length){
				window.empty_gear.style = "display:none";
			}
			else{
				window.empty_gear.style = "display:initial";
			}
			//buttons
			for(let [btn,display] of Object.entries(msg.buttons)){
				window[btn].style = "display:"+display
			}
			//ship
			if(pdata.img !== ship.src){
				ship.src = pdata.img
			}
			ship.style = "transform: rotate("+String(rotation)+"deg);"
			//station
			if(Object.keys(msg.structure).length && msg.structure.image){
				ship.style.display = "none"
			}
			else{
				ship.style.display = "initial"
			}
		}
		else if(e.target.status===400){
			console.log(e.target.response)
		}
		else if(e.target.status===401){
			window.location.href = "/login.html"
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}

function do_move(e){
	var cell = e.target
	if(cell.nodeName === "IMG"){cell = cell.parentNode}
	var [x,y] = position
	var x2 = x+cell.coord_x
	var y2 = y+cell.coord_y
	send({"command":"move","position":[x2,y2]})
}
function do_gather(){
	send({"command":"gather"})
}
function do_dropall(){
	send({"command":"drop","items":items})
}

send({"command":"get-location"})

var ship = document.createElement("img")
grid[0][0].append(ship)

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
window.navigate.click()