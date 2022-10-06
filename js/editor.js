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
		grid[x][y].style.color=invertColour(c)
		terrain[x][y].color = c
	}
	if(s){
		if(s==="empty"){s=""}
		grid[x][y].innerHTML=s
		terrain[x][y].string = s
		c = terrain[x][y].color || colors["blue"]
		grid[x][y].style.color=invertColour(c)
	}
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

var colors = {
	"blue":"#0000FF",
	"deepskyblue":"#00bfff",
	"black":"#000000",
	"red":"#ff0000",
	"grey":"#808080",
	"lawngreen":"#7cfc00",
}
var strings = [
	"empty",
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

var current_colour=""
var current_string=""
var activeColour=""
var activeTextBtn
strings.forEach(s=>{
	var button=document.createElement("button")
	button.innerHTML=s
	button.onclick=()=>{current_string=s;current_colour=""}
	button.setAttribute("class","text")
	button.addEventListener("click", function() {
		if(activeColourBtn){
			activeColourBtn.style.borderColor = activeColour
			activeColourBtn.style.backgroundColor = "white"
			activeColourBtn.style.color="black"
		}
		if(activeTextBtn){
			activeTextBtn.style.backgroundColor="white"
			activeTextBtn.style.color="black"
		}
		activeTextBtn=this
		activeTextBtn.style.backgroundColor="black"
		activeTextBtn.style.color="white"
	})
	button.style.color = "black"
	button.style.backgroundColor = "white"
	window.text.append(button)
})
Object.keys(colors).forEach(c=>{
	var button=document.createElement("button")
	button.innerHTML=c
	button.onclick=()=>{current_colour=colors[c];current_string=""}
	button.setAttribute("class","colour")
	button.addEventListener("click", function() {
		if(activeTextBtn){
			activeTextBtn.style.backgroundColor="white"
			activeTextBtn.style.color="black"
		}
		activeColourBtn.style.borderColor = activeColour
		activeColourBtn.style.backgroundColor = "white"
		activeColourBtn.style.color="black"
		activeColourBtn=this
		activeColour=colors[c]
		activeColourBtn.style.backgroundColor=colors[c]
		activeColourBtn.style.color=invertColour(colors[c])
		activeColourBtn.style.borderColor=colors[c]
	})
	button.style.borderColor = colors[c]
	button.style.backgroundColor = "white"
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

function click_tile(e){
	if(e.target.nodeName === "TD"){
		var cell = e.target
		setTile(cell.coord_x,cell.coord_y,current_colour,current_string)
	}
}