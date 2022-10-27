const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.nav_button.onclick = ()=>window.location.href = "/nav.html"+window.location.search
window.sell_all.onclick = do_sellall
forClass("tablinks",e=>{
	e.onclick = open_tab
})

var pdata = {}
var inv = {}
var items = {}
var gear = {}
var credits = 0
var structure = {}
var sinv = {}
var itypes = {}

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
			console.log(pdata,structure,itypes)
			update_trade()
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
function update_trade(){
	if(!active_itype){
		active_itype = Object.keys(itypes)[0]
	}
	window.itemtypes.innerHTML = ""
	Object.keys(itypes).forEach(it=>{
		var btn = addElement(window.itemtypes,"button",it)
		btn.onclick = ()=>{
			active_itype = it
			update_trade()
		}
	})
	forClass("ship_credits",e=>e.innerHTML = "Credits: "+credits)
	forClass("structure_credits",e=>e.innerHTML = "Credits: "+structure.credits)
	forClass("ship_space",e=>e.innerHTML = "Space: "+inv.space_left+"/"+(inv.space_max+inv.space_extra))
	forClass("structure_space",e=>e.innerHTML = "Space: "+sinv.space_left+"/"+(sinv.space_max+sinv.space_extra))
	clear_table("sell")
	clear_table("buy")
	make_headers("sell")
	make_headers("buy")
	for(let [item,data] of Object.entries(structure.market.prices)){
		if(itypes[active_itype].includes(item)){
			make_row("sell",item,items[item]||0,data.buy)
			make_row("buy",item,structure.inventory.items[item]||0,data.sell)
		}
	}
	for(let [item,data] of Object.entries(structure.inventory.gear)){
		if(item in items){
			make_row("sell",item,items[item]||0,structure.inventory.gear[item].buy)
		}
	}
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
	addElement(parent,"th","price")
	addElement(parent,"th",name)
}
function make_gear_headers(){
	var parent = window["gear_table"]
	addElement(parent,"th","name")
	addElement(parent,"th","description")
	addElement(parent,"th","size")
	addElement(parent,"th","owned")
	addElement(parent,"th","sell price")
	addElement(parent,"th","buy price")
	addElement(parent,"th","sell")
	addElement(parent,"th","buy")
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

window.transfer_button.onclick=transfer
function transfer(){
	function make_list(name){
		var inputs = Array.from(document.getElementsByClassName("item_"+name))
		var list = inputs.map(b=>Math.floor(Number(b.value))>0?{[b.item]:Math.floor(Number(b.value))}:null).filter(b=>b)
		return Object.assign({},...list)
	}
	var buyeded=make_list("buy")
	var seldeded=make_list("sell")
	var sad_dictionary={
		"bought":buyeded,
		"sold":seldeded
	}
	var message=JSON.stringify(sad_dictionary)
	console.log(message)
	send("trade-goods",{"buy":buyeded,"sell":seldeded})
}

function do_sellall(){
	var sell = {}
	for(let [item,amount] of Object.entries(items)){
		sell[item] = amount
	}
	send("trade-goods",{"buy":{},"sell":sell})
}

function open_tab(e) {
	var tabName = e.target.innerHTML
	forClass("tabcontent",el=>{
		el.style.display = "none"
	})
	forClass("tablinks",el=>{
		el.className = el.className.replace(" active", "")
	})
	document.getElementById(tabName).style.display = ""
	e.currentTarget.className += " active"
}
function forClass(name,func){
	Array.from(document.getElementsByClassName(name)).forEach(func)
}
document.getElementsByClassName("tablinks")[0].click()
send("get-goods")
