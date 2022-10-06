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

function send(table){
	table.key = key
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

var happiness = ["cat","dog","chocolate","cake","coffee","book"]

function addElement(parent,type,inner){
	var e = document.createElement(type)
	if(inner!==undefined){e.innerHTML=inner}
	parent.append(e)
	return e
}
function make_table(name){
	var parent = window[name+"_table"]
	addElement(parent,"th","name")
	addElement(parent,"th","amount")
	addElement(parent,"th","price").setAttribute("colspan","2")
	happiness.forEach(h=>{
		var row = document.createElement("tr")
		addElement(row,"td",h).setAttribute("class","name")
		addElement(row,"td",0)
		addElement(row,"td",0)
		var amount=addElement(row,"td")
		var input=addElement(amount,"input")
		amount.setAttribute("class","input")
		input.setAttribute("class",name+"_input")
		input.item=h
		input.setAttribute("min","1")
		input.setAttribute("type","number")
		parent.appendChild(row)
	})
}
make_table("buy")
make_table("sell")
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
	send({"command":"trade-goods","buy":{},"sell":sell})
}

send({"command":"get-goods"})
