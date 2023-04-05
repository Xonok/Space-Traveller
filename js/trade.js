var f=func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

f.forClass("tablinks",e=>e.onclick = open_tab)
f.forClass("tabcontent",e=>e.style.display = "none")
var active
var msg = {}
var bp_info = {}
var cdata = {}
var pship
var inv = {}
var items = {}
var gear = {}
var structure = {}
var sinv = {}
var itypes = {}
var quest_list = {}
var idata = {}
var iprices = {}
var pships = {}
var station_def = {}
var ship_defs = {}
var industry_defs = {}
var repair_fees = {}
var transfer = {
	buy: {},
	sell: {},
	reset: ()=>{
		transfer.buy = {},
		transfer.sell = {},
		window.transfer_info_text.innerHTML = ""
	}
}

var first_message = true
function send(command,table={},testing=false){
	table.key = key
	table.command = command
	if(selected_ship){
		table.ship = selected_ship.name
	}
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(testing){return}
		if(e.target.status===200){
			f.forClass("error_display",error=>{
				error.innerHTML=""
			})
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url+window.location.search
				return
			}
			msg = JSON.parse(e.target.response)
			console.log(msg)
			bp_info = msg.bp_info
			cdata = msg.cdata
			pship = msg.ship
			inv = pship.inventory
			items = inv.items
			gear = inv.gear
			structure = msg.structure
			sinv = structure.inventory
			itypes = msg.itypes
			shipdef = msg.shipdef
			quest_list = msg.quests
			idata = msg.idata
			iprices = msg.prices
			pships = msg.ships
			station_def = msg.station_def
			ship_defs = msg.ship_defs
			industry_defs = msg.industry_defs
			repair_fees = msg.repair_fees
			transfer.reset()
			make_buttons()
			window.owner.innerHTML = "Structure owner: " +structure.owner
			if(msg.quest_end_text){
				end_quest()
			}
			update()
		}
		else if(e.target.status===400 || e.target.status===500){
			if(first_message){
				window.server_error.style.display = "block"
			}
			else{
				var active_tab=active.innerHTML
				f.forClass("error_display",div=>div.innerHTML = e.target.response)
			}
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
		first_message = false
	}
	req.send(jmsg)
}

function update(){
	update_trade()
	update_manage()
	update_ship_list()
	update_repair()
	update_tabs()
	update_quests()
	update_pop()
	update_blueprints()
	update_stats()
}
var active_itype
function make_buttons(){
	if(!active_itype){
		active_itype = Object.keys(itypes)[0]
	}
	window.itemtabs.innerHTML = ""
	Object.keys(itypes).forEach(it=>{
		var btn = f.addElement(window.itemtabs,"button",it)
		if(it===active_itype){btn.className=" active_itemtab"}
		btn.onclick = ()=>{
			active_itype = it
			f.forClass("active_itemtab",el=>{
				el.className = el.className.replace(" active_itemtab", "")
			})
			btn.className += " active_itemtab"
			update_trade()
		}
	})
}
var dict_words={"drone":"drones","expander":"expanders","factory":"factories","gun":"guns","habitation":"habitations","drone1":"drone","expander1":"expander","factory1":"factory","gun1":"gun","habitation1":"habitation","module":"modules","module1":"module","shield1":"shield","shield":"shields","armor1":"armor","armor":"armors","expander1":"expander","expander":"expanders","hive_homeworld_return1":"return device","hive_homeworld_return":"return devices","field1":"field","field":"fields"}
function update_trade(){
	f.forClass("ship_credits",e=>e.innerHTML = "Credits: "+f.formatNumber(cdata.credits))
	f.forClass("structure_credits",e=>e.innerHTML = "Credits: "+f.formatNumber(structure.credits))
	f.forClass("ship_space",e=>e.innerHTML = "Space left: "+f.formatNumber(inv.space_left)+"/"+f.formatNumber((inv.space_max+inv.space_extra)))
	f.forClass("structure_space",e=>e.innerHTML = "Space left: "+f.formatNumber(sinv.space_left)+"/"+f.formatNumber((sinv.space_max+sinv.space_extra)))
	clear_tables()
	f.headers(window.sell_table,"img","name","amount","price","size","sell")
	f.forClass("active_itemtab",c=>{
		var choice = c.innerHTML === "commodity" ? ["change"] : []
		f.headers(window.buy_table,"img","name","amount",...choice,"price","size","buy")
	})
	f.headers(window.items_off,"img","name","amount","size","transfer")
	f.headers(window.items_on,"img","name","amount","size","transfer")
	f.headers(window.items_ship,"img","name","amount","size","transfer")
	f.headers(window.items_shipgear,"img","name","amount","size","transfer")
	f.headers(window.items_station,"img","name","amount","size","change","transfer")
	f.headers(window.items_stationgear,"img","name","amount","size","transfer")
	window.structure_name.innerHTML = structure.name+"<br>"+station_def.name
	f.forClass("info_display",e=>{
		e.innerHTML = "<br>"+"Next tick in: "+String(Math.floor(msg.next_tick))+" seconds."
	})
	window.item_stats.innerHTML="This station can equip: "
	for(let [key,value] of Object.entries(station_def.slots)){
		if(dict_words[key]===undefined){throw new Error("Unknown structure slot name: "+key)}
		if(value===1){var word=dict_words[key+"1"]}
		else{var word=dict_words[key]}
		window.item_stats.innerHTML+="</br>"+"* "+value+" "+word
	}
	for(let [item,data] of Object.entries(iprices)){
		if(itypes[active_itype].includes(item)){
			make_row("sell",item,items[item]||0,data.buy,idata[item].size)
			let change = structure.market.change[item]||0
			if(change > 0){
				change = "+"+change
			}
			f.forClass("active_itemtab",c=>{if(c.innerHTML!=="commodity"){change=undefined}})
			make_row2("buy",item,structure.inventory.items[item]||0,change,data.sell,idata[item].size)
		}
	}
	for(let [item,amount] of Object.entries(items)){
		make_item_row("off",item,amount||0,idata[item].size)
		make_item_row("ship",item,amount||0,idata[item].size)
	}
	for(let [item,amount] of Object.entries(gear)){
		make_item_row("on",item,amount||0,idata[item].size)
		make_item_row("shipgear",item,amount||0,idata[item].size)
	}
	for(let [item,amount] of Object.entries(sinv.items)){
		let change = structure.market.change[item]||0
		if(change > 0){
			change = "+"+change
		}
		make_item_row2("station",item,amount||0,idata[item].size,change)
	}
	for(let [item,amount] of Object.entries(sinv.gear)){
		make_item_row("stationgear",item,amount||0,idata[item].size)
	}
}
function update_manage(){
	var parent = window.trade_setup
	f.headers(parent,"item","price(buy","price(sell")
}
window.trade_setup.add_row = (e)=>{
	f.row(window.trade_setup,f.input(),f.input(0,f.only_numbers),f.input(0,f.only_numbers))
}
function update_repair(){
	var stats = selected_ship.stats
	var hull_lost = stats.hull.max - stats.hull.current
	var armor_lost = stats.armor.max - stats.armor.current
	window.current_hull.innerHTML = "Hull: "+stats.hull.current+"/"+stats.hull.max
	window.current_armor.innerHTML = "Armor: "+stats.armor.current+"/"+stats.armor.max
	window.current_shield.innerHTML = "Shield: "+stats.shield.current+"/"+stats.shield.max
	window.hull_repair_cost.innerHTML = "Cost: "+(repair_fees.hull*hull_lost)
	window.armor_repair_cost.innerHTML = "Cost: "+(repair_fees.armor*armor_lost)
}
var selected_ship_btn
var selected_ship
function update_ship_list(){
	window.ship_list.innerHTML = ""
	window.twitter.innerHTML = ""
	
	if(!selected_ship){
		selected_ship = pship
	}
	for(let s of Object.values(pships)){
		if(cdata.ships.includes(s.name)){
			var ship_list = window.ship_list
		}
		else{
			var ship_list = window.twitter
		}
		let btn = f.addElement(ship_list,"button",s.name)
		btn.style.marginLeft = "10px"
		btn.style.textAlign="left"
		btn.onclick = ()=>{
			if(selected_ship_btn){
				selected_ship_btn.style.backgroundColor = ""
			}
			selected_ship = s
			selected_ship_btn = btn
			btn.style.backgroundColor = "#ffac59"
			if(selected_ship.name !== pship.name){
				pship = s
				inv = pship.inventory
				items = inv.items
				gear = inv.gear
				update()
			}
			window.ship_stat.innerHTML="This ship can equip: "
			for(let [key,value] of Object.entries(ship_defs)){
				if(selected_ship_btn.innerHTML.includes(key)){
					for(let [key2,value2] of Object.entries(value.slots)){
						if(dict_words[key2]===undefined){throw new Error("Unknown ship slot name: "+key2)}
						if(value2===1){var word2=dict_words[key2+"1"]}
						else{var word2=dict_words[key2]}
						window.ship_stat.innerHTML+="</br>"+"* "+value2+" "+word2
					}
				}
			}
		}
		if(selected_ship && selected_ship.name === s.name){
			btn.click()
		}
	}
	if(!selected_ship){
		window.ship_list.childNodes[0].click()
	}
}
function update_tabs(){
	f.forClass("tablinks",(t)=>{
		t.style.display = "block"
		var display = (name,check)=>{
			if(t.innerHTML !== name){return}
			t.style.display = check ? "block" : "none"
		}
		display("Quests",structure.type === "planet")
		display("Trade",Object.keys(iprices).length)
		display("Equipment",structure.owner !== cdata.name)
		display("Items",structure.owner === cdata.name)
		display("Manage",structure.owner === cdata.name)
		display("Population",structure.population.workers)
		display("Construction",structure.owner === cdata.name)
		if(!active && t.style.display !== "none"){
			t.click()
		}
	})
}
var active_quest
function end_quest(){
	window.quest_desc.innerHTML = msg.quest_end_text
	window.quest_objectives.innerHTML = ""
	window.cancel_quest.style = "display: none;" 
	window.submit_quest.style = "display: none;" 
}
function update_quests(){
	window.quest_selection.innerHTML = ""
	Object.values(quest_list).forEach(q=>{
		console.log(q)
		var outcome = q.outcome
		var qbutton = f.addElement(window.quest_selection,"button",q.title+"<br>")
		var sneak_peek=f.addElement(qbutton,"label",q.desc_short)
		sneak_peek.style="font-size:10px;"
		qbutton.style="border:solid #ff8531 1px;padding:10px; background-color:#ffac59;width:200px;"
		qbutton.onclick = e=>{
			active_quest=qbutton
			if(cdata.quests_completed[q.name]){
				end_quest()
				return
			}
			window.quest_icon.setAttribute("src",q.icon)
			window.quest_title.innerHTML=q.title
			window.quest_desc.innerHTML=q.start_text
			var goals = window.quest_objectives
			goals.innerHTML = ""
			if(!cdata.quests[q.name]){
				q.outcome.objectives_text.forEach(ot=>{
					f.addElement(goals,"li",ot)
				})
			}
			else{
				q.objectives.forEach(ot=>{
					if(ot.completed){
						f.addElement(goals,"li","<del>"+ot.desc+"</del>")
					}
					else{f.addElement(goals,"li",ot.desc+": "+ot.status)}
				})
			}
			window.selected_quest.style = "display: initial; background-color:#ffac59;"
			window.accept_quest.style = cdata.quests[q.name] ? "display: none;" : "display: initial;"
			window.cancel_quest.style = cdata.quests[q.name] ? "display: initial;" : "display: none;" 
			window.submit_quest.style = cdata.quests[q.name] ? "display: initial;" : "display: none;" 
			window.accept_quest.onclick = ()=>{
				send("quest-accept",{"quest-id":q.name})
			}
			window.cancel_quest.onclick = ()=>{
				send("quest-cancel",{"quest-id":q.name})
			}
			window.submit_quest.onclick = ()=>{
				send("quest-submit",{"quest-id":q.name})
			}
		}
		active_quest?.click()
	})
}
function update_pop(){
	window.workers.innerHTML = "Workers: "+String(structure.population.workers)
	if(structure.population.max_pop){
		window.workers.innerHTML += "/"+String(structure.population.max_pop)
	}
	window.industries.innerHTML = "Industries: "+(String(Object.keys(industry_defs)) || "None")
}
var selected_blueprint
function update_blueprints(){
	if(structure.blueprints){
		var construct = window.construct
		construct.innerHTML = ""
		f.headers(construct,"name","progress","status")
		structure.builds?.forEach(b=>{
			var row = f.addElement(construct,"tr")
			f.addElement(row,"td",idata[b.blueprint].name.replace(" Blueprint",""))
			var box = f.addElement(row,"td")
			var bar = f.addElement(box,"progress")
			bar.value = b.labor
			bar.max = b.labor_needed
			f.addElement(row,"td",b.active ? "active" : "paused")
		})
		var bps = window.blueprints
		bps.innerHTML = ""
		structure.blueprints.forEach(b=>{
			var btn = f.addElement(bps,"button",idata[b].name.replace(" Blueprint",""))
			btn.onclick = ()=>{
				var info = bp_info[b]
				window.bp_name.innerHTML = idata[b].name.replace(" Blueprint","")
				var initial = window.inital
				initial.innerHTML = ""
				f.addElement(initial,"label","Initial materials needed:")
				var list = f.addElement(initial,"ul")
				Object.entries(info.inputs).forEach(i=>{
					f.addElement(list,"li",i[1]+" "+i[0])
				})
				window.ongoing.innerHTML = ""
				var result = window.result
				result.innerHTML = ""
				f.addElement(result,"label","Result")
				var list3 = f.addElement(result,"ul")
				Object.entries(info.outputs).forEach(i=>{
					f.addElement(list3,"li",i[1]+" "+i[0])
				})
				window.build.onclick = ()=>{
					send("start-build",{"blueprint":b})
				}
			}
			
		})
	}
	var i_bps = window.inventory_blueprints
	i_bps.innerHTML = ""
	Object.keys(pship.inventory.items).forEach(i=>{
		var data = idata[i]
		if(data.type==="blueprint"){
			var div = f.addElement(i_bps,"div",data.name)
			div.onclick = ()=>{
				selected_blueprint = i
			}
		}
	})
}
function update_stats(){
	var def = ship_defs[pship.type]
	var parent = window.ship_stats
	var stats = pship.stats
	func.row(parent,"size",stats.size)
	func.row(parent,"speed",stats.speed)
	func.row(parent,"agility",stats.agility)
	func.row(parent,"hull",stats.hull.current+"/"+stats.hull.max)
	func.row(parent,"armor",stats.armor.current+"/"+stats.armor.max)
	func.row(parent,"shield",stats.shield.current+"/"+stats.shield.max)
	var slots = {}
	for(let [key,value] of Object.entries(def.slots)){
		slots[key] = {
			current: 0,
			max: value
		}
	}
	Object.entries(pship.inventory.gear).forEach(item=>{
		var name = item[0]
		var amount = item[1]
		var def = idata[name]
		var slot = def.slot || def.type
		slots[slot].current += amount
	})
	parent = window.ship_slots
	for(let [key,value] of Object.entries(slots)){
		var word_key = value.current > 1 ? key : key+"1"
		func.row(parent,dict_words[word_key],value.current+"/"+value.max)
	}
}
function clear_tables(){
	Array.from(document.getElementsByTagName("table")).forEach(e=>{
		if(e.id==="ships" || e.id==="ship_offers"|| e.id==="construct"){return}
		e.innerHTML = ""
	})
}
function transfer_info(e){
	f.only_numbers(e)
	if(e.target.classList.contains("item_sell")){
		transfer.sell[e.target.item] = Number(e.target.value)
		if(!transfer.sell[e.target.item]){
			delete transfer.sell[e.target.item]
		}
	}
	else if(e.target.classList.contains("item_buy")){
		transfer.buy[e.target.item] = Number(e.target.value)
		if(!transfer.buy[e.target.item]){
			delete transfer.buy[e.target.item]
		}
	}
	var s = ""
	if(Object.entries(transfer.sell).length){s += "Selling: <br>"}
	Object.entries(transfer.sell).forEach(data=>{
		item = data[0]
		amount = data[1]
		s += String(amount)+" "+idata[item].name+"<br>"
	})
	if(Object.entries(transfer.buy).length){s += "Buying: <br>"}
	Object.entries(transfer.buy).forEach(data=>{
		item = data[0]
		amount = data[1]
		s += String(amount)+" "+idata[item].name+"<br>"
	})
	window.transfer_info_text.innerHTML = s
}
function make_input(parent,name,item,func){
	var input = f.addElement(parent,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.saved_value = 0
	input.item = item
	input.oninput = func
	return input
}
function make_row(name,item,amount,price,size){
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.setAttribute("class","item_amount "+name)
	f.addElement(row,"td",f.formatNumber(price)).setAttribute("class","item_price "+name)
	f.addElement(row,"td",size)
	var input = make_input(row,name,item,transfer_info)
	amount_div.onclick = ()=>{
		input.value = amount
		transfer_info({"target":input})
	}
	parent.appendChild(row)
}
function make_row2(name,item,amount,change,price,size){
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.setAttribute("class","item_amount "+name)
	if(change!==undefined){
		var change_div = f.addElement(row,"td",change)
		change_div.onclick = ()=>{
			if(change < 0){
				var opposite_table_dict={"buy":"sell"}
				var opposite_table=opposite_table_dict[name]
				if(!opposite_table){throw new Error("Unknown table: " + name)}
				f.forClass(opposite_table,b=>{if(b.item===item){b.value=f.formatNumber(Number(b.value)+Math.abs(change))}})
			}
		}
	}
	f.addElement(row,"td",f.formatNumber(price)).setAttribute("class","item_price "+name)
	f.addElement(row,"td",size).setAttribute("class","item_size "+name)
	var input = make_input(row,name,item,transfer_info)
	amount_div.onclick = ()=>{
		input.value = amount
		transfer_info({"target":input})
	}
	parent.appendChild(row)
}
function make_item_row(name,item,amount,size){
	var parent = window["items_"+name]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.setAttribute("class","item_amount "+name)
	f.addElement(row,"td",size).setAttribute("class","item_size "+name)
	var input = make_input(row,name,item,f.only_numbers)
	amount_div.onclick = ()=>{
		input.value = amount
		transfer_info({"target":input})
	}
	parent.appendChild(row)
}
function make_item_row2(name,item,amount,size,change){
	var parent = window["items_"+name]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.setAttribute("class","item_amount "+name)
	f.addElement(row,"td",size).setAttribute("class","item_amount "+name)
	var change_div = f.addElement(row,"td",change)
	var input = make_input(row,name,item,f.only_numbers)
	change_div.onclick = ()=>{
		if(change[0]==="+"){input.value = f.formatNumber(Number(input.value)+Number(change.substring(1, change.length)))}
		if(change < 0){
			var opposite_table_dict={"on":"item_off","station":"item_ship","stationgear":"item_shipgear"}
			var opposite_table=opposite_table_dict[name]
			if(!opposite_table){throw new Error("Unknown table: " + name)}
			f.forClass(opposite_table,b=>{
				if(b.item===item){b.value=f.formatNumber(Number(b.value)+Number(Math.abs(change)))}
			})
		}
	}
	amount_div.onclick = ()=>{
		input.value = amount
		transfer_info({"target":input})
	}
	parent.appendChild(row)
}
function make_list(name){
	var inputs = Array.from(document.getElementsByClassName(name))
	var list = inputs.map(b=>Math.floor(Number(b.value))>0?{[b.item]:Math.floor(Number(b.value))}:null).filter(b=>b)
	return Object.assign({},...list)
}
var do_transfer = ()=>send("trade-goods",{"buy":transfer.buy,"sell":transfer.sell})
function do_transfer2(){
	var give = make_list("item_ship")
	var take = make_list("item_station")
	var give_gear = make_list("item_shipgear")
	var take_gear = make_list("item_stationgear")
	send("transfer-goods",{"take":take,"give":give,"take_gear":take_gear,"give_gear":give_gear})
}
function do_transfer_credits(){
	var give = Math.floor(Number(window.give_credits.value))
	var take = Math.floor(Number(window.take_credits.value))
	give && take && f.forClass("error_display",e=>e.innerHTML="Can't both give and take credits at the same time.")
	give && !take && send("give-credits",{"amount":give})
	take && !give && send("take-credits",{"amount":take})
	window.give_credits.value = 0
	window.take_credits.value = 0
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
function do_equip_blueprint(){
	if(selected_blueprint){
		send("equip-blueprint",{"blueprint":selected_blueprint})
	}
}
function do_repair_hull(){
	var stats = selected_ship.stats
	var hull_lost = stats.hull.max - stats.hull.current
	send("repair",{"ship":selected_ship.name,"hull":hull_lost,"armor":0})
}
function do_repair_armor(){
	var stats = selected_ship.stats
	var armor_lost = stats.armor.max - stats.armor.current
	send("repair",{"ship":selected_ship.name,"hull":0,"armor":armor_lost})
}
function do_update_trade_prices(){
	var table = {}
	window.trade_setup.childNodes.forEach(r=>{
		if(r.type === "headers"){return}
		var name = r.childNodes[0].childNodes[0].value
		var buy = Number(r.childNodes[1].childNodes[0].value)
		var sell = Number(r.childNodes[2].childNodes[0].value)
		if(!name || (!buy && !sell)){return}
		table[name] = {
			buy: buy,
			sell: sell
		}
	})
	if(!Object.keys(table).length){}
	send("update-trade",{"items":table})
}

function open_tab(e) {
	var tabName = e.target.innerHTML
	active = e.target
	f.forClass("tabcontent",el=>{
		el.style.display = "none"
	})
	f.forClass("tablinks",el=>{
		el.className = el.className.replace(" active", "")
	})
	document.getElementById(tabName).style.display = ""
	e.currentTarget.className += " active"
	if(tabName!=="Trade"){
		window.itemtabs.setAttribute("style","display: none")
	}
	else{window.itemtabs.setAttribute("style","display: block")}
}
function test(times){
	console.time("testing")
	var x = 0
	var intervalID = setInterval(()=>{
		send("get-goods",{},true)
		if (++x === times) {
			window.clearInterval(intervalID)
			console.timeEnd("testing")
		}
	},1)
}

window.transfer_button.onclick = do_transfer
window.transfer_button2.onclick = do_transfer2
window.transfer_credits.onclick = do_transfer_credits
window.sell_all.onclick = do_sellall
window.store_all.onclick = do_storeall
window.take_all.onclick = do_takeall
window.equip.onclick = do_equip
window.equip2.onclick = do_equip2
window.equip_blueprint.onclick = do_equip_blueprint
window.repair_hull.onclick = do_repair_hull
window.repair_armor.onclick = do_repair_armor
window.trade_setup_add_row.onclick = window.trade_setup.add_row
window.give_credits.onblur = f.only_numbers
window.take_credits.onblur = f.only_numbers
window.update_trade_prices.onclick = do_update_trade_prices

send("get-goods")
