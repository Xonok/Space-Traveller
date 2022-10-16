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
window.unequip.onclick = do_unequip


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
			window.station_space.innerHTML = station.space_max-station.space+"/"+station.space_max
			console.log(msg)
			clear_table("ship")
			clear_table("station")
			clear_gear_table("ship")
			clear_gear_table("station")
			make_headers("ship")
			make_headers("station")
			for(let [item,amount] of Object.entries(items)){
				make_row("ship",item,amount||0)
			}
			for(let [item,amount] of Object.entries(station.items)){
				make_row("station",item,amount||0)
			}
			make_gear_headers("ship")
			make_gear_headers("station")
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
	window[name+"_table"].innerHTML = ""
}
function clear_gear_table(name){
	window[name+"_gear"].innerHTML = ""
}
function make_headers(name){
	var parent = window[name+"_table"]
	addElement(parent,"th","name")
	addElement(parent,"th","amount")
	addElement(parent,"th","transfer")
	addElement(parent,"th","equip")
}
function make_gear_headers(name){
	var parent = window[name+"_gear"]
	addElement(parent,"th","name")
	addElement(parent,"th","amount")
	addElement(parent,"th","unequip")
}
function only_numbers(e){
	var el = e.target
	var val = Number(el.value)
	if(isNaN(val)){
		el.value=el.saved_value
	}
}
function make_row(name,item,amount){
	var parent = window[name+"_table"]
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
	var td2 = addElement(row,"td")
	var input2 = addElement(td2,"input")
	input2.setAttribute("class","equip_"+name+" "+name)
	input2.value = 0
	input2.item = item
	input2.saved_value = input.value
	input2.onchange = only_numbers
	parent.appendChild(row)
}
function make_gear_row(name,item,amount){
	var parent = window[name+"_gear"]
	var row = document.createElement("tr")
	addElement(row,"td",item)
	addElement(row,"td",amount)
	var td = addElement(row,"td")
	var input = addElement(td,"input")
	input.setAttribute("class","unequip_"+name+" "+name)
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
	var give=make_list("item_ship")
	var take=make_list("item_station")
	send("transfer-goods",{"take":take,"give":give})
}
function do_storeall(){
	var give = {}
	for(let [item,amount] of Object.entries(items)){
		give[item] = amount
	}
	send("transfer-goods",{"take":{},"give":give})
}
function do_takeall(){
	var take = {}
	for(let [item,amount] of Object.entries(station.items)){
		take[item] = amount
	}
	send("transfer-goods",{"take":take,"give":{}})
}
function do_equip(){
	var ship_on = make_list("equip_ship")
	var station_on = make_list("equip_station")
	send("equip",{"ship-on":ship_on,"station-on":station_on,"ship-off":{},"station-off":{}})
}
function do_unequip(){
	var ship_off = make_list("unequip_ship")
	var station_off = make_list("unequip_station")
	send("equip",{"ship-on":{},"station-on":{},"ship-off":ship_off,"station-off":station_off})
}

send("get-goods")
