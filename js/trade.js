const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.nav_button.onclick = ()=>window.location.href = "/nav.html"+window.location.search
window.quests.onclick = ()=>window.location.href = "/quests.html"+window.location.search
window.editor.onclick = ()=>window.location.href = "/editor.html"+window.location.search
window.forum.onclick = ()=>window.location.href = "/forum.html"+window.location.search
window.chat.onclick = ()=>window.location.href = "/chat.html"+window.location.search
window.transfer_button.onclick = do_transfer
window.transfer_button2.onclick = do_transfer2
window.sell_all.onclick = do_sellall
window.store_all.onclick = do_storeall
window.take_all.onclick = do_takeall
window.equip.onclick = do_equip
window.equip2.onclick = do_equip2
forClass("tablinks",e=>{
	e.onclick = open_tab
})
forClass("tabcontent",el=>{
	el.style.display = "none"
})
var active

var pdata = {}
var inv = {}
var items = {}
var gear = {}
var credits = 0
var structure = {}
var sinv = {}
var itypes = {}
var quest_list = {}

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
			pdata = msg.pdata
			inv = msg.pdata.inventory
			items = inv.items
			gear = inv.gear
			credits = pdata.credits
			structure = msg.structure
			sinv = structure.inventory
			itypes = msg.itypes
			shipdef = msg.shipdef
			quest_list = msg.quests
			console.log(pdata,structure,itypes,shipdef,quest_list)
			window.structure_name.innerHTML = structure.name
			make_buttons()
			update_trade()
			update_tabs()
			update_quests()
			update_pop()
			if(!active){
				Array.from(document.getElementsByClassName("tablinks")).forEach(e=>{
					if(e.className.includes(" active")){
						
					}
				})//.click()
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

var active_itype
function make_buttons(){
	if(!active_itype){
		active_itype = Object.keys(itypes)[0]
	}
	window.itemtabs.innerHTML = ""
	Object.keys(itypes).forEach(it=>{
		var btn = addElement(window.itemtabs,"button",it)
		btn.onclick = ()=>{
			active_itype = it
			update_trade()
		}
	})
}
function update_trade(){
	forClass("ship_credits",e=>e.innerHTML = "Credits: "+credits)
	forClass("structure_credits",e=>e.innerHTML = "Credits: "+structure.credits)
	forClass("ship_space",e=>e.innerHTML = "Space: "+inv.space_left+"/"+(inv.space_max+inv.space_extra))
	forClass("structure_space",e=>e.innerHTML = "Space: "+sinv.space_left+"/"+(sinv.space_max+sinv.space_extra))
	clear_tables()
	make_headers("sell")
	make_headers("buy")
	make_item_headers("items_off")
	make_item_headers("items_on")
	make_item_headers("items_ship")
	make_item_headers("items_shipgear")
	make_item_headers("items_station")
	make_item_headers("items_stationgear")
	for(let [item,data] of Object.entries(structure.market.prices)){
		if(itypes[active_itype].includes(item)){
			make_row("sell",item,items[item]||0,data.buy)
			make_row("buy",item,structure.inventory.items[item]||0,data.sell)
		}
	}
	for(let [item,amount] of Object.entries(items)){
		make_item_row("off",item,amount||0)
		make_item_row("ship",item,amount||0)
	}
	for(let [item,amount] of Object.entries(gear)){
		make_item_row("on",item,amount||0)
		make_item_row("shipgear",item,amount||0)
	}
	for(let [item,amount] of Object.entries(sinv.items)){
		make_item_row("station",item,amount||0)
	}
	for(let [item,amount] of Object.entries(sinv.gear)){
		make_item_row("stationgear",item,amount||0)
	}
}
function update_tabs(){
	window.forClass("tablinks",(t)=>{
		t.style.display = "block"
		if(t.innerHTML === "Quests"){
			t.style.display = structure.type === "planet" ? "block" : "none"
		}
		if(t.innerHTML === "Trade"){
			t.style.display = Object.keys(structure.market.prices).length ? "block" : "none"
		}
		if(t.innerHTML === "Equipment"){
			t.style.display = structure.owner !== pdata.name ? "block" : "none"
		}
		if(t.innerHTML === "Items"){
			t.style.display = structure.owner === pdata.name ? "block" : "none"
		}
		if(t.innerHTML === "Population"){
			t.style.display = structure.population.workers ? "block" : "none"
		}
		if(t.innerHTML === "Construction"){
			t.style.display = structure.owner === pdata.name ? "block" : "none"
		}
		if(!active && t.style.display !== "none"){
			t.click()
		}
	})
}
function update_quests(){
	window.quest_selection.innerHTML = ""
	Object.values(quest_list).forEach(q=>{
		console.log(q)
		var qdiv = addElement(window.quest_selection,"div",q.title+"<br>"+q.desc_short)
		qdiv.onclick = e=>{
			window.selected_quest.innerHTML = q.start_text
			window.accept_quest.style = "display: initial;"
			window.cancel_quest.style = "display: initial;"
		}
	})
}
function update_pop(){
	window.workers.innerHTML = "Workers: "+String(structure.population.workers)
	window.industries.innerHTML = "Industries: "+String(structure.population.industries)
}

function addElement(parent,type,inner){
	var e = document.createElement(type)
	if(inner!==undefined){e.innerHTML=inner}
	parent.append(e)
	return e
}
function clear_tables(){
	Array.from(document.getElementsByTagName("table")).forEach(e=>e.innerHTML = "")
}
function make_headers(name){
	var parent = window[name+"_table"]
	addElement(parent,"th","name")
	addElement(parent,"th","amount")
	addElement(parent,"th","price")
	addElement(parent,"th",name)
}
function make_item_headers(name){
	var parent = window[name]
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
function make_row(name,item,amount,price){
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	addElement(row,"td",item).setAttribute("class","item_name "+name)
	addElement(row,"td",amount).setAttribute("class","item_amount "+name)
	addElement(row,"td",price).setAttribute("class","item_price "+name)
	var input = addElement(row,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.item = item
	input.saved_value = input.value
	input.onchange = only_numbers
	parent.appendChild(row)
}
function make_item_row(name,item,amount){
	var parent = window["items_"+name]
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
function make_gear_row(item,data){
	var parent = window["gear_table"]
	var row = document.createElement("tr")
	addElement(row,"td",data.name)
	addElement(row,"td",data.desc)
	addElement(row,"td",data.size)
	addElement(row,"td",get_player_gear(item))
	addElement(row,"td",data.buy)
	addElement(row,"td",data.sell)
	var a = addElement(row,"td")
	var b = addElement(row,"td")
	a.setAttribute("class","no_padding")
	b.setAttribute("class","no_padding")
	var sell = addElement(a,"button","Sell")
	var buy = addElement(b,"button","Buy")
	sell.setAttribute("class","no_padding no_border full_width square button")
	buy.setAttribute("class","no_padding no_border full_width square button")
	sell.onclick = ()=>{send("sell-gear",{"gear":item})}
	buy.onclick = ()=>{send("buy-gear",{"gear":item})}
	parent.appendChild(row)
}
function make_list(name){
	var inputs = Array.from(document.getElementsByClassName(name))
	var list = inputs.map(b=>Math.floor(Number(b.value))>0?{[b.item]:Math.floor(Number(b.value))}:null).filter(b=>b)
	return Object.assign({},...list)
}
function do_transfer(){
	var buyeded=make_list("buy")
	var seldeded=make_list("sell")
	send("trade-goods",{"buy":buyeded,"sell":seldeded})
}
function do_transfer2(){
	var give = make_list("item_ship")
	var take = make_list("item_station")
	var give_gear = make_list("item_shipgear")
	var take_gear = make_list("item_stationgear")
	console.log(give,take,give_gear,take_gear)
	send("transfer-goods",{"take":take,"give":give,"take_gear":take_gear,"give_gear":give_gear})
}

function do_sellall(){
	var sell = {}
	for(let [item,amount] of Object.entries(items)){
		if(itypes[active_itype].includes(item)){
			sell[item] = amount
		}
	}
	send("trade-goods",{"buy":{},"sell":sell})
}
function do_equip(){
	var equip = make_list("off")
	var unequip = make_list("on")
	send("equip",{"ship-on":equip,"ship-off":unequip,"station-on":{},"station-off":{}})
}
function do_equip2(){
	var ship_on = make_list("item_ship")
	var station_on = make_list("item_station")
	var ship_off = make_list("item_shipgear")
	var station_off = make_list("item_stationgear")
	send("equip",{"ship-on":ship_on,"station-on":station_on,"ship-off":ship_off,"station-off":station_off})
}
function do_storeall(){
	send("transfer-goods",{"take":{},"give":items,"take_gear":{},"give_gear":{}})
}
function do_takeall(){
	send("transfer-goods",{"take":structure.inventory.items,"give":{},"take_gear":{},"give_gear":{}})
}

function open_tab(e) {
	var tabName = e.target.innerHTML
	active = e
	forClass("tabcontent",el=>{
		el.style.display = "none"
	})
	forClass("tablinks",el=>{
		el.className = el.className.replace(" active", "")
	})
	document.getElementById(tabName).style.display = ""
	e.currentTarget.className += " active"
	if(tabName!=="Trade"){
		window.itemtabs.setAttribute("style","display: none")
	}
	else{window.itemtabs.setAttribute("style","display: block")}
}
function forClass(name,func){
	Array.from(document.getElementsByClassName(name)).forEach(func)
}

send("get-goods")
