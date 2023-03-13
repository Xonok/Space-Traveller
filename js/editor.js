var map = window.space_map

var grid = {}
function draw(tiles_x,tiles_y,initial=false){
	if(!initial){
		localSave()
	}
	tiles_x = Number(tiles_x)
	tiles_y = Number(tiles_y)
	clear()
	map.innerHTML = ""
	var x_min = Math.floor(-(tiles_x-1)/2)
	var x_max = Math.floor((tiles_x+1)/2)
	var y_min = Math.floor(-(tiles_y-1)/2)
	var y_max = Math.floor((tiles_y+1)/2)
	grid = {}
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
	if(!initial){
		localLoad()
	}
}
draw(40,25,true)
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
		"tiles": cleanTable(structuredClone(terrain),["structure"])
	}
	var objmap = {
		"name": window.filename.value,
		"tiles": cleanTable(structuredClone(terrain),["object","terrain"])
	}
	console.log(system)
	console.log(objmap)
	saveText(window.filename.value+"_map",system)
	saveText(window.filename.value+"_objs",objmap)
}
var saved_map
function localSave(){
	saved_map = JSON.stringify({
		"name": window.filename.value,
		"tiles": structuredClone(terrain)
	})
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
function localLoad(){
	if(saved_map){load(saved_map)}
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
window.new_map_size.onclick = (e)=>draw(window.x.value,window.y.value)
window.clear_map.onclick = clear

var terrains = {
	"deep_energy":"#0000FF",
	"energy":"#00bfff",
	"space":"#000000",
	"nebula":"#ff0000",
	"asteroids":"#808080",
	"exotic":"#7cfc00",
	"phase":"#ffa500"
}
var colorname = {
	"rgb(0, 0, 255)":"Blue",
	"rgb(0, 191, 255)":"LightBlue",
	"rgb(0, 0, 0)":"Black",
	"rgb(255, 0, 0)":"Red",
	"rgb(128, 128, 128)":"Grey",
	"rgb(124, 252, 0)":"Green",
	"rgb(255, 165, 0)":"Yellow"
}
var shapes = ["iclu","icru","icld","icrd","oclu","ocru","ocld","ocrd","full","su","sd","sr","sl"]

var current_mode

var active_color
Object.keys(terrains).forEach(t=>{
	var button=document.createElement("button")
	button.setAttribute("class","colour")
	button.addEventListener("click", function() {
		activeColourBtn.style.borderWidth="5px"
		activeColourBtn=this
		activeColourBtn.style.borderWidth="1px"
		current_mode = "terrain"
		selected_terrain = t
		make_shapes(t)
		
	})
	button.style.borderWidth="5px"
	button.style.backgroundColor = terrains[t]
	button.style.width="30px"
	button.style.height="30px"
	window.colour.append(button)
})
var activeColourBtn=document.getElementsByClassName("colour")[2]
activeColourBtn.click()

function make_shapes(t){
	window.shape.innerHTML=""
	if(t==="deep_energy"){return}
	Object.keys(shapes).forEach(s=>{
		var button=document.createElement("button")
		button.setAttribute("class","shape img-size")
		var img= func.addElement(button,"img")
		var color=colorname[activeColourBtn.style.backgroundColor]
		button.addEventListener("click", function() {
			activeShapeBtn.style.borderWidth="0px"
			activeShapeBtn=this
			activeShapeBtn.style.borderWidth="3px"
			current_mode = "terrain"
			selected_shape = s
		})
		
		button.childNodes.forEach(n=>n.setAttribute("src","../img/tiles/"+color+"/"+shapes[s]+".png"))
		window.shape.append(button)
	})
}
var activeShapeBtn=document.getElementsByClassName("colour")[2]

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
function setTerrain(x,y,t,s){
	if(t === undefined){return}
	if(s === undefined){console.log("setTerrain shape missing")}
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
				setTerrain(x,y,selected_terrain,selected_shape)
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