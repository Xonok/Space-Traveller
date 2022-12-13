var map = window.space_map

var tiles_x = 40
var tiles_y = 25
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
function cleanTable(table,removes){
	if(!removes || !removes.length){
		throw new Exception("Cleaning a table requires a list of key names to remove")
	}
	var new_table = {}
	for(let [key,value] of Object.entries(table)){
		if(!removes.includes(key)){
			if(!Array.isArray(value) && typeof value === "object" && value){
				value = cleanTable(value,removes)
				if(!Object.entries(value).length){
					value = null
				}
			}
			if(value !== null && value !== undefined){
				new_table[key] = value
			}
		}
	}
	return new_table
}
function saveText(fname,data){
	var content = JSON.stringify(data,null,"\t")
	var filename = fname+".json"
	var pom = document.createElement('a')
	pom.setAttribute('href','data:text/json;charset=utf-8,'+encodeURIComponent(content))
	pom.setAttribute('download',filename)

	if(document.createEvent){
		var event = document.createEvent('MouseEvents')
		event.initEvent('click',true,true)
		pom.dispatchEvent(event)
	}
	else{
		pom.click()
	}
}
function save(){
	var system = {
		"name": window.filename.value,
		"tiles": cleanTable(structuredClone(terrain),["object","structure"])
	}
	var objmap = {
		"name": window.filename.value,
		"tiles": cleanTable(structuredClone(terrain),["terrain"])
	}
	console.log(system)
	console.log(objmap)
	saveText(window.filename.value+"_map",system)
	saveText(window.filename.value+"_objs",objmap)
}
function load(data){
	var table = JSON.parse(data)
	console.log(table)
	for (let [x,column] of Object.entries(table.tiles)){
		for(let [y,cell] of Object.entries(column)){
			setTerrain(x,y,cell.terrain)
			setStructure(x,y,cell.structure)
			setWormhole(x,y,cell.object)
		}
	}
	window.filename.value = table.name
}
function load_e(e){
	var reader = new FileReader()
	reader.onload = ()=>{load(reader.result)}
	reader.readAsText(e.target.files[0])
}
function clear(){
	terrain = {}
	var tds = Array.from(document.getElementsByTagName("td"))
	tds.forEach(td=>{
		td.style.backgroundColor = "blue"
		td.innerHTML = ""
	})
}

var drawing = false
map.onmousedown = ()=> drawing = true
map.onmouseup = ()=> drawing = false
map.onmousemove = click_tile
map.onclick = click_tile
save_btn.onclick = ()=>save()
load_btn.onclick = ()=>window.load_input.click()
load_input.onchange = load_e
window.clear_map.onclick = clear

var terrains = {
	"deep_energy":"#0000FF",
	"energy":"#00bfff",
	"space":"#000000",
	"nebula":"#ff0000",
	"asteroids":"#808080",
	"exotic":"#7cfc00",
}

var current_mode

Object.keys(terrains).forEach(t=>{
	var button=document.createElement("button")
	button.setAttribute("class","colour")
	button.addEventListener("click", function() {
		activeColourBtn.style.borderWidth="1px"
		activeColourBtn.style.color="black"
		activeColourBtn=this
		activeColourBtn.style.borderColor="white"
		activeColourBtn.style.borderWidth="5px"
		current_mode = "terrain"
		selected_terrain = t
	})
	button.style.borderColor = terrains[t]
	button.style.backgroundColor = terrains[t]
	button.style.width="30px"
	button.style.height="30px"
	window.colour.append(button)
})
var activeColourBtn=document.getElementsByClassName("colour")[2]
activeColourBtn.click()

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

function checkTile(x,y){
	if(!terrain[x]){
		terrain[x] = {}
	}
	if(!terrain[x][y]){
		terrain[x][y] = {}
	}
}
function clearTile(x,y){
	if(!Object.keys(terrain[x][y]).length){
		delete terrain[x][y]
	}
	if(!Object.keys(terrain[x]).length){
		delete terrain[x]
	}
}
function setTerrain(x,y,t){
	if(t === undefined){return}
	grid[x][y].style.backgroundColor = terrains[t]
	grid[x][y].style.color=invertColour(terrains[t])
	checkTile(x,y)
	terrain[x][y].terrain = t
	if(t === "deep_energy"){
		delete terrain[x][y].terrain
	}
	clearTile(x,y)
}
function setStructure(x,y,s){
	if(s===undefined){return}
	checkTile(x,y)
	var grid_tile = grid[x][y]
	var map_tile = terrain[x][y]
	delete map_tile.object
	map_tile.structure = s
	if(!s){
		delete map_tile.structure
	}
	grid_tile.innerHTML = s
	grid_tile.innerHTML = "blah"
	clearTile(x,y)
}
function setWormhole(x,y,w){
	if(w===undefined){return}
	checkTile(x,y)
	var grid_tile = grid[x][y]
	var map_tile = terrain[x][y]
	delete map_tile.structure
	map_tile.object = w
	if(!w){
		delete map_tile.object
	}
	grid_tile.innerHTML = w
	clearTile(x,y)
}

function click_tile(e){
	if(!drawing && e.type !== "click"){return}
	if(e.target.nodeName === "TD"){
		var x = e.target.coord_x
		var y = e.target.coord_y
		switch(current_mode){
			case "terrain":
				setTerrain(x,y,selected_terrain)
				break
			case "structure":
				setStructure(x,y,window.structure_input.value)
				break
			case "wormhole":
				setWormhole(x,y,window.wormhole_input.value)
				break
		}
	}
}
var radio_content=[terrain_content,structure_content,wormhole_content]
function click_radio(input){
	current_mode = input.id
	radio_content.forEach(c=>window[c.id].style= "display:none;")
	var something=input.id+"_content"
	window[something].style = "display:initial;"

}