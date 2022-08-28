var map = window.space_map

var tiles_x = 20
var tiles_y = 20
var x_min = Math.floor(-(tiles_x-1)/2)
var x_max = Math.floor((tiles_x+1)/2)
var y_min = Math.floor(-(tiles_y-1)/2)
var y_max = Math.floor((tiles_y+1)/2)
for(let y = y_min;y<y_max;y++){
	var row = document.createElement("tr")
	for(let x = x_min;x<x_max;x++){
		var cell = document.createElement("td")
		cell.coord_x = x
		cell.coord_y = y
		row.append(cell)
	}
	map.append(row)
}
var terrain = {}
for(let x = x_min;x<x_max;x++){
	terrain[x] = {}
	for(let y = y_min;x<y_max;y++){
		terrain[x][y] = {"color":"blue","string":""}
	}
}

map.onclick = click_tile

var colors = [
	"blue",
	"deepskyblue",
	"black",
	"red",
	"grey",
	"lawngreen",
]

function click_tile(e){
	if(e.target.nodeName === "TD"){
		var cell = e.target
		if(editor_mode=="tile_mode"){
			var prev_color = cell.style.backgroundColor || "blue"
			var color_id = colors.indexOf(prev_color)
			var new_color = colors[(color_id+1)%colors.length]
			cell.style.backgroundColor = new_color
			terrain[cell.coord_x][cell.coord_y].color = new_color
		}
	}
}