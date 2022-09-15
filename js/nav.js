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

