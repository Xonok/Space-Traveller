/*
CODE STATUS - version 2, needs improvement.
Version 1 was the original proof of concept.
Version 2 changed UI, enabled split maps(_map and _objs), and added support for tile images.
*Maybe the canvas size should be in the map file.
*Maybe constellation and starmap data should be in the map file.
*Newer features are not supported:
**props entry like in Academy_map
*/

var f = func

var map = window.space_map

var grid = {}
var grid_width, grid_height 
function draw(tiles_x,tiles_y,initial=false){
	!initial && localSave()
	tiles_x = Number(tiles_x)
	tiles_y = Number(tiles_y)
	grid_width = tiles_x
	grid_height = tiles_y
	clear()
	map.innerHTML = ""
	var x_min = Math.floor(-(tiles_x-1)/2)
	var x_max = Math.floor((tiles_x+1)/2)
	var y_min = Math.floor(-(tiles_y-1)/2)
	var y_max = Math.floor((tiles_y+1)/2)
	grid = {}
	for(let y = y_min;y<y_max;y++){
		if(y == y_min){
			var top_row = document.createElement("tr")
			f.addElement(top_row,"th")
			for(let x = x_min;x<x_max;x++){
				f.addElement(top_row,"th",String(x))
			}
			map.append(top_row)
		}
		var row = document.createElement("tr")
		for(let x = x_min;x<x_max;x++){
			if(x == x_min){
				f.addElement(row,"th",-y)
			}
			if(!grid[x]){grid[x]={}}
			var cell = document.createElement("td")
			cell.coord_x = x
			cell.coord_y = -y
			row.append(cell)
			grid[x][-y] = cell
		}
		map.append(row)
	}
	if(!initial){
		localLoad()
	}
}
if(!window.x.value || !window.y.value){
	window.x.value = 40
	window.y.value = 25
}
draw(window.x.value,window.y.value,true)
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
function saveText(fname,props,tiles){
	var data = {
		"name": fname
	}
	if(props && Object.entries(props).length){
		data["props"] = props
	}
	data["tiles"] = tiles
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
	saveText(window.filename.value,window.map_props,terrain)
}
var saved_map
function localSave(){
	saved_map = JSON.stringify({
		"name": window.filename.value,
		"props": window.map_props,
		"tiles": structuredClone(terrain)
	})
}
function load(data){
	var table = JSON.parse(data)
	var reduce = (table,func)=>Object.keys(table).reduce((a,k)=>func(a,Number(k)),0)
	var xs = [...Object.keys(table.tiles)]
	var ys = xs.map(x=>Object.keys(table.tiles[x])).flat().filter((e,i,a)=>a.indexOf(e)===i)
	if(!xs.length || !ys.length){return}
	var x_min = Math.min(...xs)
	var x_max = Math.max(...xs)
	var y_min = Math.min(...ys)
	var y_max = Math.max(...ys)
	var width = Math.max(x_max*2,x_min*-2)+1
	var height = Math.max(y_max*2,y_min*-2)+1
	if(grid_width < width || grid_height < height){
		var new_width = Math.max(grid_width,width)
		var new_height = Math.max(grid_height,height)
		console.log("Loaded map is too big. Resizing grid to ",new_width,",",new_height)
		draw(new_width,new_height)
	}
	for (let [x,column] of Object.entries(table.tiles)){
		for(let [y,cell] of Object.entries(column)){
			change_stamp(cell.terrain,cell.variation,cell.structure,cell.wormhole)
			apply_stamp(x,y,"terrain")
			apply_stamp(x,y,"structure")
			apply_stamp(x,y,"wormhole")
		}
	}
	window.map_props = table["props"] || window.map_props
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
		td.style.backgroundImage = null
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
window.clear_map.onclick = ()=>{
	console.log("Clearing map.")
	clear()
	window.props = undefined
	if(grid_width > window.x.value || grid_height > window.y.value){
		console.log("Resizing grid to what the last specified size was.")
		draw(window.x.value,window.y.value)
	}
}

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
var shapes = ["full","iclu","icru","icld","icrd","oclu","ocru","ocld","ocrd","su","sd","sr","sl"]

var current_mode
var selected_terrain
var selected_shape

var stamp = {
	mode: "terrain",
	terrain: "energy",
	variation: "full",
	structure: get_structure(),
	wormhole: get_wormhole()
}

function get_tile(map,x,y){
	return map[x]?.[y] || {}
}
function set_tile(map,x,y,tile){
	if(!map[x]){
		map[x] = {}
	}
	map[x][y] = tile
	if(!Object.keys(map[x][y]).length){
		delete map[x][y]
	}
	if(!Object.keys(map[x]).length){
		delete map[x]
	}
}
function get_structure(){
	return window.structure_input.value || null
}
function get_wormhole(){
	return {
		"type": window.wormhole_input.value,
		"target": {
			"x": Number(window.wormhole_x.value),
			"y": Number(window.wormhole_y.value),
			"rotation": 0,
			"system": window.wormhole_system.value
		}
	}
}
function change_stamp(terrain,variation,structure,wormhole){
	stamp.terrain = terrain !== null ? terrain : stamp.terrain
	stamp.variation = variation !== null ? variation : stamp.variation
	stamp.structure = structure !== null ? structure : stamp.structure
	stamp.wormhole = wormhole !== null ? wormhole : stamp.wormhole
	if(stamp.structure === ""){stamp.structure = undefined}
	if(stamp.wormhole?.type === ""){stamp.wormhole = undefined}
	//console.log(stamp,variation)
}
function apply_stamp(x,y,mode=stamp.mode){
	var logic_tile = get_tile(terrain,x,y)
	var visual_tile = get_tile(grid,x,y)
	var variation = stamp.variation
	if(stamp.terrain === "space" || stamp.terrain === "deep_energy"){
		variation = null
	}
	if(mode === "terrain" && stamp.terrain){
		visual_tile.style.backgroundColor = terrains[stamp.terrain]
		var color = colorname[visual_tile.style.backgroundColor]
		visual_tile.style.color = invertColour(terrains[stamp.terrain])
		if(variation){
			visual_tile.style.backgroundImage = "url(img/tiles/"+color+"/"+variation+".png)"
		}
		else{
			visual_tile.style.backgroundImage = null
		}
		logic_tile.terrain = stamp.terrain || logic_tile.terrain
		logic_tile.variation = variation || logic_tile.variation
		if(stamp.terrain === "deep_energy"){
			logic_tile = {}
			visual_tile.innerHTML = ""
			visual_tile.style.backgroundImage = null
		}
	}
	if(mode === "structure" && stamp.structure !== undefined && logic_tile.terrain){
		if(stamp.structure || (logic_tile.structure && !stamp.structure)){
			logic_tile.structure = stamp.structure
			visual_tile.innerHTML = stamp.structure
		}
	}
	if(mode === "wormhole" && stamp.wormhole !== undefined && logic_tile.terrain){
		if(stamp.wormhole || (logic_tile.wormhole && !stamp.wormhole)){
			logic_tile.wormhole = stamp.wormhole
			visual_tile.innerHTML = stamp.wormhole.target?.system || stamp.wormhole.type
		}
	}
	set_tile(terrain,x,y,logic_tile)
}

Object.keys(terrains).forEach(t=>{
	var button=document.createElement("button")
	button.setAttribute("class","colour")
	button.addEventListener("click", function() {
		activeColourBtn=this
		// this.className="active_editorbutton"
		stamp.mode = "terrain"
		change_stamp(t,null,null,null)
		make_shapes(t)
	})
	// button.classList.remove("active_editorbutton")
	button.style.backgroundColor = terrains[t]
	button.style.width="30px"
	button.style.height="30px"
	window.colour.append(button)
	
})
var activeColourBtn=document.getElementsByClassName("colour")[1]
activeColourBtn.click()

function make_shapes(t){
	window.shape.innerHTML=""
	if(t==="deep_energy" || t === "space"){return}
	Object.keys(shapes).forEach(s=>{
		var button=document.createElement("button")
		button.setAttribute("class","shape img-size")
		var img= func.addElement(button,"img")
		var color=colorname[activeColourBtn.style.backgroundColor]
		button.addEventListener("click", function() {
			activeShapeBtn=this
			stamp.mode = "terrain"
			change_stamp(t,shapes[s],null,null)
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

function click_tile(e){
	if(!drawing && e.type !== "click"){return}
	if(e.target.nodeName === "TD"){
		if(stamp.mode === "terrain" && !stamp.variation){stamp.variation="full"}
		if(stamp.mode === "structure"){stamp.structure=get_structure()}
		if(stamp.mode === "wormhole"){stamp.wormhole=get_wormhole()}
		apply_stamp(e.target.coord_x,e.target.coord_y)
	}
}
var radio_content=[terrain_content,structure_content,wormhole_content]
function click_radio(input){
	stamp.mode = input.id
	radio_content.forEach(c=>window[c.id].style= "display:none;")
	var something=input.id+"_content"
	window[something].style = "display:initial;"
}
window.structure_input.onchange = e=>stamp.structure = get_structure()
window.wormhole_input.onchange = e=>stamp.wormhole = get_wormhole()