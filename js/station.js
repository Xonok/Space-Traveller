const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.nav_button.onclick = ()=>window.location.href = "/nav.html"+window.location.search
window.transfer_button.onclick = do_transfer

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
			station = msg.station
			window.ship_space.innerHTML = pdata.space_total-pdata.space_available+"/"+pdata.space_total
			window.station_space.innerHTML = station.space_max-station.space+"/"+station.space_max
			console.log(msg)
			clear_table("ship")
			clear_table("station")
			make_headers("ship")
			make_headers("station")
			for(let [item,amount] of Object.entries(items)){
				make_row("ship",item,amount||0)
			}
			for(let [item,amount] of Object.entries(station.items)){
				make_row("station",item,amount||0)
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
function make_headers(name){
	var parent = window[name+"_table"]
	addElement(parent,"th","name")
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
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	addElement(row,"td",item).setAttribute("class","item_name "+name)
	addElement(row,"td",amount).setAttribute("class","item_amount "+name)
	var input = addElement(row,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.item = item
	input.saved_value = input.value
	input.onchange = only_numbers
	parent.appendChild(row)
}
function get_player_gear(item){
	return gear[item] || 0
}
function do_transfer(){
	function make_list(name){
		var inputs = Array.from(document.getElementsByClassName("item_"+name))
		var list = inputs.map(b=>Math.floor(Number(b.value))>0?{[b.item]:Math.floor(Number(b.value))}:null).filter(b=>b)
		return Object.assign({},...list)
	}
	var give=make_list("ship")
	var take=make_list("station")
	var dict={
		"give":give,
		"take":take
	}
	var message=JSON.stringify(dict)
	console.log(message)
	send("transfer-goods",{"take":take,"give":give})
}

send("get-goods")
