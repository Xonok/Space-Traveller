const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.nav_button.onclick = ()=>window.location.href = "/nav.html"+window.location.search
window.transfer_button.onclick = do_transfer
window.store_all.onclick = do_storeall
window.take_all.onclick = do_takeall
window.equip.onclick = do_equip


var items = {}
var gear = {}
var credits = 0
var market = {}
var station = {}

function send(command,table={}){
	table.key = key
	table.command = command 
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url+window.location.search
				return
			}
			var msg = JSON.parse(e.target.response)
			var pdata = msg.pdata
			items = msg.items
			gear = msg.gear
			station = msg.station
			window.ship_space.innerHTML = pdata.space_total-pdata.space_available+"/"+pdata.space_total
			window.station_space.innerHTML = station.space_max+station.space_extra-station.space+"/"+String(Number(station.space_max)+Number(station.space_extra))
			console.log(msg)
			clear_table("ship_items")
			clear_table("station_items")
			clear_table("ship_gear")
			clear_table("station_gear")
			make_headers("ship_items")
			make_headers("station_items")
			for(let [item,amount] of Object.entries(items)){
				make_row("ship",item,amount||0)
			}
			for(let [item,amount] of Object.entries(station.items)){
				make_row("station",item,amount||0)
			}
			make_headers("ship_gear")
			make_headers("station_gear")
			for(let [item,amount] of Object.entries(gear)){
				make_gear_row("ship",item,amount||0)
			}
			for(let [item,amount] of Object.entries(station.gear)){
				make_gear_row("station",item,amount||0)
			}
		}
		else if(e.target.status===401){
			console.log(e.target)
			//window.location.href = "/login.html"
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}

function addElement(parent,type,inner){
	var e = document.createElement(type)
	if(inner!==undefined){e.innerHTML=inner}
	parent.append(e)
	return e
}
function clear_table(name){
	window[name].innerHTML = ""
}
function make_headers(name){
	var parent = window[name]
	addElement(parent,"th","name").setAttribute("style","min-width:100px;")
	addElement(parent,"th","amount")
	addElement(parent,"th","transfer")
}
function only_numbers(e){
	var el = e.target
	var val = Number(el.value)
	if(isNaN(val)){
		el.value=el.saved_value
	}
}
function make_row(name,item,amount){
	var parent = window[name+"_items"]
	var row = document.createElement("tr")
	addElement(row,"td",item)
	addElement(row,"td",amount)
	var td = addElement(row,"td")
	var input = addElement(td,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.item = item
	input.saved_value = input.value
	input.onchange = only_numbers
	parent.appendChild(row)
}
function make_gear_row(name,item,amount){
	var parent = window[name+"_gear"]
	var row = document.createElement("tr")
	addElement(row,"td",item)
	addElement(row,"td",amount)
	var td = addElement(row,"td")
	var input = addElement(td,"input")
	input.setAttribute("class","gear_"+name+" "+name)
	input.value = 0
	input.item = item
	input.saved_value = input.value
	input.onchange = only_numbers
	parent.appendChild(row)
}
function get_player_gear(item){
	return gear[item] || 0
}
function make_list(name){
	var inputs = Array.from(document.getElementsByClassName(name))
	var list = inputs.map(b=>Math.floor(Number(b.value))>0?{[b.item]:Math.floor(Number(b.value))}:null).filter(b=>b)
	return Object.assign({},...list)
}
function do_transfer(){
	var give = make_list("item_ship")
	var take = make_list("item_station")
	var give_gear = make_list("gear_ship")
	var take_gear = make_list("gear_station")
	send("transfer-goods",{"take":take,"give":give,"take_gear":take_gear,"give_gear":give_gear})
}
function do_storeall(){
	send("transfer-goods",{"take":{},"give":items,"take_gear":{},"give_gear":{}})
}
function do_takeall(){
	send("transfer-goods",{"take":station.items,"give":{},"take_gear":{},"give_gear":{}})
}
function do_equip(){
	var ship_on = make_list("item_ship")
	var station_on = make_list("item_station")
	var ship_off = make_list("gear_ship")
	var station_off = make_list("gear_station")
	send("equip",{"ship-on":ship_on,"station-on":station_on,"ship-off":ship_off,"station-off":station_off})
}

send("get-goods")
