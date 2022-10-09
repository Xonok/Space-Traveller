const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.nav_button.onclick = ()=>window.location.href = "/nav.html"+window.location.search
window.sell_all.onclick = do_sellall

var items = {}
var credits = 0
var market = {}

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
			items = pdata.items
			credits = pdata.credits
			market = msg.market
			console.log(items,credits,market)
			clear_table("sell")
			clear_table("buy")
			make_headers("sell")
			make_headers("buy")
			for(let [item,data] of Object.entries(market.items)){
				make_row("sell",item,items[item]||0,data.buy)
				make_row("buy",item,data.amount,data.sell)
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
	addElement(parent,"th","price")
	addElement(parent,"th",name)
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
	var fields = {}
	addElement(row,"td",item).setAttribute("class","item_name "+name)
	addElement(row,"td",amount).setAttribute("class","item_amount "+name)
	addElement(row,"td",price).setAttribute("class","item_price "+name)
	var input = addElement(row,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.saved_value = input.value
	input.onchange = only_numbers
	parent.appendChild(row)
}

window.transfer_button.onclick=transfer
function transfer(){
	function make_list(name){//need support for pi and stuff
		var inputs = Array.from(document.getElementsByClassName(name+"_input"))
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
}

function do_sellall(){
	var sell = {}
	for(let [item,amount] of Object.entries(items)){
		sell[item] = amount
	}
	send("trade-goods",{"buy":{},"sell":sell})
}

send("get-goods")
