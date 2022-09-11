var map = window.space_map

var tiles_x = 20
var tiles_y = 20
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
function checkTile(x,y){
	if(!terrain[x]){terrain[x] = {}}
	if(!terrain[x][y]){terrain[x][y] = {}}
}
function clearTile(x,y){
	var c = terrain[x][y].color
	var s = terrain[x][y].string
	if(!c || c==="blue" && !s){
		delete terrain[x][y]
	}
	if(!Object.keys(terrain[x]).length){
		delete terrain[x]
	}
}
function setTile(x,y,c,s){
	checkTile(x,y)
	if(c){
		grid[x][y].style.backgroundColor = c
		terrain[x][y].color = c
	}
	if(s){terrain[x][y].string = s}
	clearTile(x,y)
}
var saved = ""
function save(){
	var data = JSON.stringify(terrain)
	var filename = window.filename.value+".json"
	saved = data
	var pom = document.createElement('a')
	pom.setAttribute('href','data:text/xml;charset=utf-8,'+encodeURIComponent(data))
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
function load(data){
	clear()
	var table = JSON.parse(data)
	for (let [x,column] of Object.entries(table)){
		for(let [y,cell] of Object.entries(column)){
			setTile(x,y,cell.color,cell.string)
		}
	}
}
function load_e(e){
	var reader = new FileReader()
	reader.onload = ()=>{load(reader.result)}
	reader.readAsText(e.target.files[0])
	window.filename.value = e.target.files[0].name.split(".")[0]
}
function clear(){
	terrain = {}
	var tds = Array.from(document.getElementsByTagName("td"))
	tds.forEach(td=>td.style.backgroundColor = "blue")
}

map.onclick = click_tile
save_btn.onclick = ()=>save()
load_btn.onclick = ()=>window.load_input.click()
load_input.onchange = load_e

var colors = [
	"blue",
	"deepskyblue",
	"black",
	"red",
	"grey",
	"lawngreen",
]
var strings = [
	"B*",//placeholder
	"SN",
	"SP",
	"SA",
	"PT",
	"PI",
	"PR",
	"PG",
	"PD",
	"ON",
	"OX",
	"OY",
	"OZ"
]

var current_colour="grey"
var current_string=""
var active_colour=""
strings.forEach(s=>{
	var button=document.createElement("button")
	button.innerHTML=s
	button.setAttribute("class","text_button")
	button.style.borderColor = "black"
	button.style.backgroundColor = "white"
	window.text.append(button)
})
colors.forEach(c=>{
	var button=document.createElement("button")
	button.innerHTML=c
	button.onclick=()=>{current_colour=c}
	button.setAttribute("class","colour_button")
	button.addEventListener("click", function() {
		active_button.style.borderColor = active_colour
		active_button.style.backgroundColor = "white"
		active_button.style.color="black"
		active_button=this
		active_colour=c
		active_button.style.backgroundColor=c
		active_button.style.color="white"
		active_button.style.borderColor=c
	})
	button.style.borderColor = c
	button.style.backgroundColor = "white"
	window.colour.append(button)
})
var active_button=document.getElementsByClassName("colour_button")[2]
active_button.click()
function click_tile(e){
	if(e.target.nodeName === "TD"){
		var cell = e.target
		cell.style.backgroundColor = current_colour
		setTile(cell.coord_x,cell.coord_y,current_colour,current_string)
	}
}