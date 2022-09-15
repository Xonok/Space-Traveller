var query = window.location.search
const url_params = new URLSearchParams(query)
const key = url_params.get('key')
if(!key){
	throw new Error("Not logged in.")
}

var map = window.space_map
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
terrain = {}

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
			var tiles = JSON.parse(e.target.response)
			for(var [x,row] of Object.entries(tiles)){
				for(var [y,tile] of Object.entries(row)){
					grid[x][y].style.backgroundColor = tile.color
					grid[x][y].style.color = invertColour(tile.color || "#0000FF")
					grid[x][y].innerHTML = tile.string || ""
				}
			}
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}

function move(x,y){
	send({"x":x,"y":y})
}

send({"command":"get-location"})

