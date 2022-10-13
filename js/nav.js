const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.gather.onclick = do_gather
window.drop_all.onclick = do_dropall
window.dock.onclick = do_dock
window.smelt.onclick = do_smelt
window.brew.onclick = do_brew
window.build.onclick = do_build
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
			var tiles = msg.tiles
			var [x,y] = pdata.position
			position = [x,y]
			for(let [x2,row] of Object.entries(tiles)){
				for(let [y2,tile] of Object.entries(row)){
					var x3 = x2-x
					var y3 = y2-y
					if(!grid[x3]?.[y3]){continue}
					grid[x3][y3].style.backgroundColor = tile.color
					grid[x3][y3].style.color = invertColour(tile.color || "#0000FF")
					if(x3 !== 0 || y3 !== 0){
						grid[x3][y3].innerHTML = tile.string || ""
					}
					if(tile.station){
						var station_img = document.createElement("img")
						station_img.src = tile.station
						station_img.station = true
						grid[x3][y3].appendChild(station_img)
					}
					else{
						Array.from(grid[x3][y3].childNodes).forEach(n=>{
							if(n.station){
								n.remove()
							}
						})
					}
					
				}
			}
			//inventory
			var inv = window.inventory
			while(inv.firstChild){
				inv.removeChild(inv.firstChild)
			}
			for(let [item,amount] of Object.entries(msg.items)){
				let tr = document.createElement("tr")
				tr.append(createElement("td",item))
				tr.append(createElement("td",String(amount)))
				inv.append(tr)
			}
			items = pdata.items
			//buttons
			for(let [btn,display] of Object.entries(msg.buttons)){
				window[btn].style = "display:"+display
			}
			//ship
			if(pdata.img !== ship.src){
				ship.src = pdata.img
			}
			ship.style = "transform: rotate("+String(pdata.rotation)+"deg);"
			//station
			if(Object.keys(msg.station).length){
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
function do_dock(){
	send({"command":"dock","position":position})
}
function do_smelt(){
	send({"command":"smelt"})
}
function do_brew(){
	send({"command":"brew"})
}
function do_build(){
	send({"command":"build"})
}

send({"command":"get-location"})

var ship = document.createElement("img")
grid[0][0].append(ship)
