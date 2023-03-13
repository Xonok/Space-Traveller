var f=func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
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
window.give_credits.onblur = only_numbers
window.take_credits.onblur = only_numbers

forClass("tablinks",e=>{
	e.onclick = open_tab
})
forClass("tabcontent",el=>{
	el.style.display = "none"
})
var active
forClass("active",a=>{
	if(a.innerHTML==="Trade"){
		console.log(a)
		a.style.borderTop="10px solid yellow"
	}
})
var msg = {}
var bp_info = {}
var cdata = {}
var pship
var inv = {}
var items = {}
var gear = {}
var credits = 0
var structure = {}
var sinv = {}
var itypes = {}
var quest_list = {}
var idata = {}
var iprices = {}
var pships = {}
var station_def = {}
var ship_def = {}
var industry_defs = {}
var repair_fees = {}

function send(command,table={}){
	table.key = key
	table.command = command
	if(selected_ship){
		table.ship = selected_ship.name
	}
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			forClass("error_display",error=>{
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
			credits = cdata.credits
			structure = msg.structure
			sinv = structure.inventory
			itypes = msg.itypes
			shipdef = msg.shipdef
			quest_list = msg.quests
			idata = msg.idata
			iprices = msg.prices
			pships = msg.ships
			station_def = msg.station_def
			ship_def = msg.ship_defs
			industry_defs = msg.industry_defs
			repair_fees = msg.repair_fees
			make_buttons()
			update()
		}
		else if(e.target.status===400){
			var active_tab=active.innerHTML
			forClass("error_display",error=>{
				error.classList.forEach(classes=>{
					if(classes==="Trade"){"Missing place for error in trade tab"}
					else if(classes===active_tab){error.innerHTML=e.target.response}
				})
			})
			console.log(e.target.response)
		}
		else if(e.target.status===500){
			forClass("error_display",error=>{
				error.classList.forEach(classes=>{
					if(classes===active_tab){error.innerHTML = "Server error."}
				})
				error.innerHTML = "Server error."
			})
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}

function update(){
	update_trade()
	update_ship_list()
	update_repair()
	update_ships()
	update_tabs()
	update_quests()
	update_pop()
	update_blueprints()
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
			forClass("active_itemtab",el=>{
				el.className = el.className.replace(" active_itemtab", "")
			})
			btn.className += " active_itemtab"
			update_trade()
		}
	})
}
function update_trade(){
	forClass("ship_credits",e=>e.innerHTML = "Credits: "+func.formatNumber(credits))
	forClass("structure_credits",e=>e.innerHTML = "Credits: "+func.formatNumber(structure.credits))
	forClass("ship_space",e=>e.innerHTML = "Space left: "+func.formatNumber(inv.space_left)+"/"+func.formatNumber((inv.space_max+inv.space_extra)))
	forClass("structure_space",e=>e.innerHTML = "Space left: "+func.formatNumber(sinv.space_left)+"/"+func.formatNumber((sinv.space_max+sinv.space_extra)))
	clear_tables()
	f.headers(window.sell_table,"img","name","amount","price","size","sell")
	forClass("active_itemtab",c=>{
		if(c.innerHTML==="commodity"){f.headers(window.buy_table,"img","name","amount","change","price","size","buy")}
		else{f.headers(window.buy_table,"img","name","amount","price","size","buy")}
	})
	f.headers(window.items_off,"img","name","amount","size","transfer")
	f.headers(window.items_on,"img","name","amount","size","transfer")
	f.headers(window.items_ship,"img","name","amount","size","transfer")
	f.headers(window.items_shipgear,"img","name","amount","size","transfer")
	f.headers(window.items_station,"img","name","amount","size","change","transfer")
	f.headers(window.items_stationgear,"img","name","amount","size","transfer")
	window.structure_name.innerHTML = structure.name+"<br>"+station_def.name
	forClass("info_display",e=>{
		e.innerHTML = "<br>"+"Next tick in: "+String(Math.floor(msg.next_tick))+" seconds."
	})
	window.item_stats.innerHTML="This station can equip: "
	var dict_words={"drone":"drones","expander":"expanders","factory":"factories","gun":"guns","habitation":"habitations","drone1":"drone","expander1":"expander","factory1":"factory","gun1":"gun","habitation1":"habitation","module":"modules","module1":"module","shield1":"shield","shield":"shields","armor1":"armor","armor":"armors","expander1":"expander","expander":"expanders"}
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
			forClass("active_itemtab",c=>{if(c.innerHTML!=="commodity"){change=undefined}})
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
function update_repair(){
	var stats = selected_ship.stats
	var hull_lost = stats.hull.max - stats.hull.current
	var armor_lost = stats.armor.max - stats.armor.current
	window.current_hull.innerHTML = "Hull: "+stats.hull.current+"/"+stats.hull.max
	window.current_armor.innerHTML = "Armor: "+stats.armor.current+"/"+stats.armor.max
	window.current_shield.innerHTML = "Shield: "+stats.shield.current+"/"+stats.shield.max
	window.hull_repair_cost.innerHTML = "Cost: "+(repair_fees.hull*hull_lost)
	window.armor_repair_cost.innerHTML = "Cost: "+(repair_fees.armor*armor_lost)
	console.log(selected_ship)
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
			var dict_words2={"gun":"guns","gun1":"gun","hive_homeworld_return1":"hive homeworld return","hive_homeworld_return":"hive homeworld return","factory":"factories","factory1":"factory","field":"fields","field1":"field","module":"modules","module1":"module","drone":"drones","drone1":"drone","shield1":"shield","shield":"shields","armor1":"armor","armor":"armors","expander1":"expander","expander":"expanders"}
			for(let [key,value] of Object.entries(ship_def)){
				if(selected_ship_btn.innerHTML.includes(key)){
					for(let [key2,value2] of Object.entries(value.slots)){
						if(dict_words2[key2]===undefined){throw new Error("Unknown ship slot name: "+key2)}
						if(value2===1){var word2=dict_words2[key2+"1"]}
						else{var word2=dict_words2[key2]}
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
function update_ships(){
	window.ships.innerHTML=""
	window.ship_offers.innerHTML=""
	f.headers(window.ships,"name","enter","items")
	f.headers(window.ship_offers,"name","price","buy")
	for(let [name,data] of Object.entries(pships)){
		if(name === pship.name){continue}
		let row = f.addElement(window.ships,"tr")
		f.addElement(row,"td",name)
		let btn_box = f.addElement(row,"td")
		f.addElement(btn_box,"button","Enter").onclick = ()=>{
			send("ship-enter",{"ship":name})
		}
		btn_box = f.addElement(row,"td")
		f.addElement(btn_box,"button","Items").onclick = ()=>{
			console.log(data.inventory)
		}
	}
	structure.ship_offers.forEach(o=>{
		let row = f.addElement(window.ship_offers,"tr")
		f.addElement(row,"td",o.ship)
		f.addElement(row,"td",String(o.price))
		let btn_box = f.addElement(row,"td")
		f.addElement(btn_box,"button","Buy").onclick = ()=>{
			send("ship-buy",{"ship":o.ship})
		}
	})
}
function update_tabs(){
	window.forClass("tablinks",(t)=>{
		t.style.display = "block"
		if(t.innerHTML === "Quests"){
			t.style.display = structure.type === "planet" ? "block" : "none"
		}
		if(t.innerHTML === "Trade"){
			t.style.display = Object.keys(iprices).length ? "block" : "none"
		}
		if(t.innerHTML === "Equipment"){
			t.style.display = structure.owner !== cdata.name ? "block" : "none"
		}
		if(t.innerHTML === "Items"){
			t.style.display = structure.owner === cdata.name ? "block" : "none"
		}
		if(t.innerHTML === "Population"){
			t.style.display = structure.population.workers ? "block" : "none"
		}
		if(t.innerHTML === "Construction"){
			t.style.display = structure.owner === cdata.name ? "block" : "none"
		}
		if(t.innerHTML === "Ships"){
			t.style.display = structure.owner === cdata.name ? "none" : "none"
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
		var qbutton = f.addElement(window.quest_selection,"button",q.title+"<br>")
		var sneak_peek=f.addElement(qbutton,"label",q.desc_short)
		sneak_peek.style="font-size:10px;"
		qbutton.style="border:solid #ff8531 1px;padding:10px; background-color:#ffac59;width:200px;"
		qbutton.onclick = e=>{
			window.quest_icon.setAttribute("src",q.icon)
			window.quest_title.innerHTML=q.title
			window.quest_desc.innerHTML=q.start_text
			var goals = window.quest_objectives
			goals.innerHTML = ""
			q.objectives_text.forEach(ot=>{
				f.addElement(goals,"li",ot)
			})
			window.selected_quest.style = "display: initial; background-color:#ffac59;"
			window.accept_quest.style = cdata.quests[q.id] ? "display: none;" : "display: initial;"
			window.cancel_quest.style = cdata.quests[q.id] ? "display: initial;" : "display: none;" 
			window.submit_quest.style = cdata.quests[q.id] ? "display: initial;" : "display: none;" 
			window.accept_quest.onclick = ()=>{
				send("quest-accept",{"quest-id":q.id})
			}
			window.cancel_quest.onclick = ()=>{
				send("quest-cancel",{"quest-id":q.id})
			}
			window.submit_quest.onclick = ()=>{
				send("quest-submit",{"quest-id":q.id})
			}
		}
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
				var ongoing = window.ongoing
				ongoing.innerHTML = ""
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
function clear_tables(){
	Array.from(document.getElementsByTagName("table")).forEach(e=>{
		if(e.id==="ships" || e.id==="ship_offers"|| e.id==="construct"){return}
		e.innerHTML = ""
	})
}
function only_numbers(e){
	var el = e.target
	var val = Number(el.value)
	if(isNaN(val)){
		el.value = el.saved_value || 0
	}
}
function formatString(s){
	return s.replaceAll("\n","<br>").replaceAll("\t","&nbsp;&nbsp;&nbsp;&nbsp;")
}
function tooltip(parent,idata){
	var txt = idata.desc
	idata.prop_info?.forEach(i=>{
		txt += "<br>"+"&nbsp;".repeat(4)
		txt += i.value ? i.key+": "+i.value : i.key
	})
	var tt = f.addElement(parent,"span",formatString(txt))
	tt.className = "tooltiptext"
	return tt
}
function make_row(name,item,amount,price,size){
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",func.formatNumber(amount))
	amount_div.setAttribute("class","item_amount "+name)
	f.addElement(row,"td",func.formatNumber(price)).setAttribute("class","item_price "+name)
	f.addElement(row,"td",size)
	var input = f.addElement(row,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.item = item
	input.saved_value = input.value
	input.onchange = only_numbers
	amount_div.onclick = ()=>{input.value = amount}
	parent.appendChild(row)
}
function make_row2(name,item,amount,change,price,size){
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",func.formatNumber(amount))
	amount_div.setAttribute("class","item_amount "+name)
	if(change!==undefined){
		var change_div = f.addElement(row,"td",change)
		change_div.onclick = ()=>{
			if(change[0]==="+"){input.value = Number(input.value)+Number(change.substring(1, change.length))}
			if(change < 0){
				var opposite_table_dict={"buy":"sell"}
				var opposite_table=opposite_table_dict[name]
				if(!opposite_table){throw new Error("Unknown table: " + name)}
				forClass(opposite_table,b=>{if(b.item===item){b.value=func.formatNumber(Number(b.value)+Math.abs(change))}})
			}
		}
	}
	f.addElement(row,"td",func.formatNumber(price)).setAttribute("class","item_price "+name)
	f.addElement(row,"td",size).setAttribute("class","item_size "+name)
	var input = f.addElement(row,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.item = item
	input.saved_value = input.value
	input.onchange = only_numbers
	amount_div.onclick = ()=>{input.value = amount}
	parent.appendChild(row)
}
function make_item_row(name,item,amount,size){
	var parent = window["items_"+name]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",func.formatNumber(amount))
	amount_div.setAttribute("class","item_amount "+name)
	f.addElement(row,"td",size).setAttribute("class","item_size "+name)
	var input = f.addElement(row,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.item = item
	input.saved_value = input.value
	input.onchange = only_numbers
	amount_div.onclick = ()=>{input.value = func.formatNumber(amount)}
	parent.appendChild(row)
}
function make_item_row2(name,item,amount,size,change){
	var parent = window["items_"+name]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",func.formatNumber(amount))
	amount_div.setAttribute("class","item_amount "+name)
	f.addElement(row,"td",size).setAttribute("class","item_amount "+name)
	var change_div = f.addElement(row,"td",change)
	var input = f.addElement(row,"input")
	input.setAttribute("class","item_"+name+" "+name)
	input.value = 0
	input.item = item
	input.saved_value = input.value
	input.onchange = only_numbers
	change_div.onclick = ()=>{
		if(change[0]==="+"){input.value = func.formatNumber(Number(input.value)+Number(change.substring(1, change.length)))}
		if(change < 0){
			var opposite_table_dict={"on":"item_off","station":"item_ship","stationgear":"item_shipgear"}
			var opposite_table=opposite_table_dict[name]
			if(!opposite_table){throw new Error("Unknown table: " + name)}
			forClass(opposite_table,b=>{
				if(b.item===item){b.value=func.formatNumber(Number(b.value)+Number(Math.abs(change)))}
			})
		}
	}
	amount_div.onclick = ()=>{input.value = amount}
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
function do_transfer_credits(){
	var give = Math.floor(Number(window.give_credits.value))
	var take = Math.floor(Number(window.take_credits.value))
	if(give && take){
		console.log("A")
		forClass("error_display",e=>{e.innerHTML="Can't both give and take credits at the same time."})
	}
	else if(give){
		console.log("B",give)
		send("give-credits",{"amount":give})
	}
	else if(take){
		console.log("C",take)
		send("take-credits",{"amount":take})
	}
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

function open_tab(e) {
	var tabName = e.target.innerHTML
	active = e.target
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
