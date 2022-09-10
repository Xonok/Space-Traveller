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
	for(let y = y_min;y<y_max;y++){
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
var current_colour="grey"
colors.forEach(c=>{
	var button=document.createElement("button")
	button.innerHTML=c
	button.onclick=()=>{colour_grid(c)}
	button.setAttribute("class",c)
	button.addEventListener("click",function(){
		var current = document.getElementsByClassName("active")
		if(current[0]){
			
			current[0].className = current[0].className.replace(" active", "")
		}
		this.className += " active";
		var active_element = document.querySelector(".active")
		active_element.style.Color = "white"
		active_element.style.backgroundColor = c
		var passive_element = document.querySelector('.'+c+':not(.active)')
		console.log()
		passive_element.style.borderColor = c
		passive_element.style.backgroundColor = "white"
	})
	window.colour.append(button)
	//var passive_element = document.querySelector('.'+c+'_button')
	//passive_element.style.borderColor = c
	//passive_element.style.backgroundColor = "white"
})
function colour_grid(colour){
	current_colour=colour
}
function click_tile(e){
	if(e.target.nodeName === "TD"){
		var cell = e.target
		cell.style.backgroundColor = current_colour
		terrain[cell.coord_x][cell.coord_y].color = current_colour
	}
}