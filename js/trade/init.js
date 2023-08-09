/*CODE STATUS - messy
*Many things should be split off.
*UI and logic code are sometimes mixed.
*Many many table functions that do essentially the same thing.
Using the table system that nav uses would be better, but it's currently not ready.
*/

var f=func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}
var active_docktab
function open_tab(e) {
	if(active_docktab){window[active_docktab].style.display="none"}
	active_docktab=e.target.innerHTML
	window[active_docktab].style.display="block"
	docktab_design()
	f.forClass("docktab",el=>{
		el.className = el.className.replace(" active", "")
	})
	e.currentTarget.className += " active"
	
}
function docktab_design(){
	if(active_docktab!=="Trade"){
		window.tradetabs.setAttribute("style","display: none")
		window.divider.style.display="initial"
		window.divider4.style.display="initial"
		window.divider5.style.display="initial"
	}
	else{
		window.tradetabs.setAttribute("style","display: block")
		window.divider.style.display="none"
		window.divider4.style.display="none"
		window.divider5.style.display="none"
	}
	if(active_docktab==="Manage"){
		window.custom_message_manage.innerHTML="In development."
	}
}
f.forClass("docktab",e=>e.onclick = open_tab)

// msg variables
var msg = {}
var bp_info = {}
var cdata = {}
var pship
var pships = {}
var inv = {}
var items = {}
var gear = {}
var structure = {}
var sinv = {}
var itypes = {}
var quest_list = {}
var idata = {}
var iprices = {}
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
			pships = msg.ships
			var local_ship = localStorage.getItem("ship")
			if(local_ship && Object.keys(pships).includes(local_ship)){
				pship = msg.ships[local_ship]
			}
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
			ship_defs = msg.ship_defs
			industry_defs = msg.industry_defs
			repair_fees = msg.repair_fees
			transfer.reset()
			make_tradetab_buttons()
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
				f.forClass("error_display",div=>{
					div.innerHTML = div.classList.contains(active_docktab) ? e.target.response : ""
				})
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

// active itemtab
var tab_message = {
	"commodity": "Trade good, make money.",
	"gun": "Shoot rocks to make money. Shoot baddies to make die.",
	"factory": "Make stuff into other stuff. Stonks. If mini, can use in inventory. Otherwise need to equip and wait up to 3 hours.",
	"ship": "No refunds, but you can buy and use as many as you want.",
	"station_kit": "Put station on map. Now you have your own smol planet.",
	"expander": "Make station go big.",
	"armor": "Much protecc, very smol, must repair for big money.",
	"shield": "Much protecc, regenerates, no repair bill."
}
var active_tradetab
function make_tradetab_buttons(){
	window.tradetabs.innerHTML = ""
	Object.keys(itypes).forEach((it,ID)=>{
		var btn = f.addElement(window.tradetabs,"button",it)
		if(it===active_tradetab){btn.className=" active_tradetab"}
		btn.onclick = ()=>{
			//css styling needs class for styling the active button differently
			f.forClass("active_tradetab",el=>{
				el.className = el.className.replace(" active_tradetab", "")
			})
			active_tradetab = it
			btn.className += " active_tradetab"
			transfer.reset()
			update_trade()
			window.custom_message.innerHTML = tab_message[active_tradetab] || ""
			window.ship_options.style.display=active_tradetab==="ship"? "initial":"none"
		}
		!ID && btn.click()
	})
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
function clear_tables(){
	Array.from(document.getElementsByTagName("table")).forEach(e=>{
		// is nessesary?
		if(e.id==="construct"){return}
		e.innerHTML = ""
	})
}
function update_trade(){
	// trade, repair, items
	f.forClass("ship_credits",e=>e.innerHTML = "Credits: "+f.formatNumber(cdata.credits))
	// trade and items
	f.forClass("structure_credits",e=>e.innerHTML = "Credits: "+f.formatNumber(structure.credits))
	f.forClass("structure_space",e=>e.innerHTML = "Space left: "+f.formatNumber(sinv.space_left)+"/"+f.formatNumber((sinv.space_max+sinv.space_extra)))
	// trade, equipment, items
	f.forClass("ship_space",e=>e.innerHTML = "Space left: "+f.formatNumber(inv.space_left)+"/"+f.formatNumber((inv.space_max+inv.space_extra)))
	// dock info
	window.structure_name.innerHTML = structure.name+"<br>"+ship_defs[structure.ship].name
	// population
	f.forClass("info_display",e=>{e.innerHTML = "<br>"+"Next tick in: "+String(Math.floor(msg.next_tick))+" seconds."})
	clear_tables()
	//trade
	f.headers(window.sell_table,"","name","count","price","size","sell")
	var choice = active_tradetab === "commodity" ? ["change"] : []
	f.headers(window.buy_table,"","name","count",...choice,"price","size","buy")
	// equipment
	f.headers(window.items_off,"","name","count","size","")
	f.headers(window.items_on,"","name","count","size","")
	// items
	f.headers(window.items_ship,"","name","count","size","")
	f.headers(window.items_shipgear,"","name","count","size","")
	f.headers(window.items_station,"","name","count","size","change","")
	f.headers(window.items_stationgear,"","name","count","size","")
	// trade
	for(let [item,data] of Object.entries(iprices)){
		if(itypes[active_tradetab].includes(item)){
			make_row("sell",item,items[item]||0,data.buy,idata[item].size,amount_click_ship)
			let change = structure.market.change[item]||0
			if(change > 0){
				change = "+"+change
			}
			f.forClass("active_tradetab",c=>{if(c.innerHTML!=="commodity"){change=undefined}})
			make_row2("buy",item,structure.inventory.items[item]||0,change,data.sell,idata[item].size,amount_click_structure)
		}
	}
	// equipment and items tab
	for(let [item,amount] of Object.entries(items)){
		make_item_row("off",item,amount||0,idata[item].size,amount_click_neutral)
		make_item_row("ship",item,amount||0,idata[item].size,amount_click_ship)
	}
	// equipment and items tab
	for(let [item,amount] of Object.entries(gear)){
		make_item_row("on",item,amount||0,idata[item].size,amount_click_neutral)
		make_item_row("shipgear",item,amount||0,idata[item].size,amount_click_ship)
	}
	for(let [item,amount] of Object.entries(sinv.items)){
		let change = structure.market.change[item]||0
		if(change > 0){
			change = "+"+change
		}
		make_item_row2("station",item,amount||0,idata[item].size,change,amount_click_structure)
	}
	for(let [item,amount] of Object.entries(sinv.gear)){
		make_item_row("stationgear",item,amount||0,idata[item].size,amount_click_structure)
	}
}
// trade sell
function make_row(name,item,amount,price,size,amount_func){
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	imgbox.classList.add("centered_")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.onmouseover=()=>{
		amount_div.style.textDecoration="underline"
	}
	amount_div.onmouseout=()=>{
		amount_div.style.textDecoration="none"
	}
	f.addElement(row,"td",f.formatNumber(price))
	f.addElement(row,"td",size)
	var input = make_input(row,name,item,transfer_info)
	amount_func(amount_div,amount,input)
	parent.appendChild(row)
}
// trade buy
function make_row2(name,item,amount,change,price,size,amount_func){
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	imgbox.classList.add("centered_")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.onmouseover=()=>{
		amount_div.style.textDecoration="underline"
	}
	amount_div.onmouseout=()=>{
		amount_div.style.textDecoration="none"
	}
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
		change_div.onmouseover=()=>{
			change_div.style.textDecoration="underline"
		}
		change_div.onmouseout=()=>{
			change_div.style.textDecoration="none"
		}
	}
	f.addElement(row,"td",f.formatNumber(price))
	f.addElement(row,"td",size)
	var input = make_input(row,name,item,transfer_info)
	amount_func(amount_div,amount,input)
	parent.appendChild(row)
}
// items, equipment 
function make_item_row(name,item,amount,size,amount_func){
	var parent = window["items_"+name]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	imgbox.classList.add("centered_")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.onmouseover=()=>{
		amount_div.style.textDecoration="underline"
	}
	amount_div.onmouseout=()=>{
		amount_div.style.textDecoration="none"
	}
	f.addElement(row,"td",size)
	var input = make_input(row,name,item,f.only_numbers)
	amount_func(amount_div,amount,input)
	parent.appendChild(row)
}
// items station items
function make_item_row2(name,item,amount,size,change,amount_func){
	var parent = window["items_"+name]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	imgbox.classList.add("centered_")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.onmouseover=()=>{
		amount_div.style.textDecoration="underline"
	}
	amount_div.onmouseout=()=>{
		amount_div.style.textDecoration="none"
	}
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
	change_div.onmouseover=()=>{
		change_div.style.textDecoration="underline"
	}
	change_div.onmouseout=()=>{
		change_div.style.textDecoration="none"
	}
	amount_func(amount_div,amount,input)
	parent.appendChild(row)
}
// manage tab, not working much
function update_manage(){
	var parent = window.trade_setup
	f.headers(parent,"item","price(buy","price(sell")
}
window.trade_setup.add_row = (e)=>{
	f.row(window.trade_setup,f.input(),f.input(0,f.only_numbers),f.input(0,f.only_numbers))
}
// manage tab end

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
		let btn = f.addElement(ship_list,"button",f.shipName(s,"character"))
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
				localStorage.setItem("ship",s.name)
				inv = pship.inventory
				items = inv.items
				gear = inv.gear
				update()
			}
			window.owner.innerHTML = "Ship: " + f.shipName(s,"character")
			
		}
		if(selected_ship && selected_ship.name === s.name){
			btn.click()
		}
	}
	if(!selected_ship){
		window.ship_list.childNodes[0].click()
	}
}

function update_repair(){
	var stats = selected_ship.stats
	var hull_lost = stats.hull.max - stats.hull.current
	var armor_lost = stats.armor.max - stats.armor.current
	if(window.repair_hull_amount.value){
		hull_lost = Math.min(hull_lost,Number(window.repair_hull_amount.value))
	}
	if(window.repair_armor_amount.value){
		armor_lost = Math.min(armor_lost,Number(window.repair_armor_amount.value))
	}
	window.repair_hull_amount.value = hull_lost
	window.repair_armor_amount.value = armor_lost
	window.current_hull.innerHTML = "Hull: "+stats.hull.current+"/"+stats.hull.max
	window.current_armor.innerHTML = "Armor: "+stats.armor.current+"/"+stats.armor.max
	window.current_shield.innerHTML = "Shield: "+stats.shield.current+"/"+stats.shield.max
	window.hull_repair_cost.innerHTML = "Cost: "+(repair_fees.hull*hull_lost)
	window.armor_repair_cost.innerHTML = "Cost: "+(repair_fees.armor*armor_lost)
}
function update_repair2(e){
	f.only_numbers(e)
	update_repair()
}

function update_tabs(){
	f.forClass("docktab",(t)=>{
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
		display("Population",structure.industries?.length)
		display("Construction",structure.owner === cdata.name)
		if(!active_docktab && t.style.display !== "none"){
			t.click()
			window[t.innerHTML].style.display="block"
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
	//Need to redo this according to the information in structure.industries
	
	//window.workers.innerHTML = "Workers: "+String(structure.population.workers)
	//if(structure.population.max_pop){
	//	window.workers.innerHTML += "/"+String(structure.population.max_pop)
	//}
	//window.industries.innerHTML = "Industries: "+(String(Object.keys(industry_defs)) || "None")
}
var selected_blueprint
var selected_blueprint_divs=[]
function update_blueprints(){
	if(structure.blueprints){
		var construct = window.construct
		construct.innerHTML = ""
		structure.builds && f.headers(construct,"name","progress","status")
		structure.builds?.forEach(b=>{
			var row = f.addElement(construct,"tr")
			f.addElement(row,"td",idata[b.blueprint].name.replace(" Blueprint",""))
			var box = f.addElement(row,"td")
			var bar = f.addElement(box,"progress")
			bar.value = b.labor
			bar.max = b.labor_needed
			f.addElement(row,"td",b.active ? "active" : "paused")
		})
		// <button>Start</button>
		// <button id="cancel">Cancel</button>
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
				window.build.innerHTML=""
				f.addElement(window.build,"button","Build")
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
			selected_blueprint_divs.push(div)
			div.onmouseover=()=>{
				div.style.cursor = "pointer"
			}
			div.onclick = ()=>{
				selected_blueprint = i
				selected_blueprint_divs.forEach(d=>{
					d.style.textDecoration="none"
				})
				div.style.textDecoration="underline"
			}
		}
	})
	if(selected_blueprint_divs.length){console.log("blueprints in inventory")}
}

var dict_words={"drone":"drones","expander":"expanders","factory":"factories","gun":"guns","habitation":"habitations","drone1":"drone","expander1":"expander","factory1":"factory","gun1":"gun","habitation1":"habitation","sensor":"sensors","sensor1":"sensor","shield1":"shield","shield":"shields","armor1":"armor","armor":"armors","expander1":"expander","expander":"expanders","aura1":"aura","aura":"auras"}
function update_slots(el,pship){
	var def = ship_defs[pship.ship || pship.type]
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
	for(let [key,value] of Object.entries(slots)){
		var word_key = value.current > 1 ? key : key+"1"
		if(value.max === -1){
			value.max = "inf"
		}
		// do we want to use the dictionary? might not be nessesary here
		if(dict_words[word_key]===undefined){throw new Error("Unknown slot")}
		func.row(el,dict_words[word_key],value.current+"/"+value.max)
	}
}

function update_stats(){
	var parent = window.ship_stats
	var stats = pship.stats
	func.row(parent,"size",stats.size)
	func.row(parent,"speed",stats.speed)
	func.row(parent,"agility",stats.agility)
	func.row(parent,"hull",stats.hull.current+"/"+stats.hull.max)
	func.row(parent,"armor",stats.armor.current+"/"+stats.armor.max)
	func.row(parent,"shield",stats.shield.current+"/"+stats.shield.max)
	update_slots(window.ship_slots,pship)
	update_slots(window.ship_stat,pship)
	console.log(structure)
	console.log(ship_defs)
	update_slots(window.item_stats,structure)
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
	input.placeholder = 0
	input.saved_value = ""
	input.item = item
	input.oninput = func
	input.onfocus = ()=>{input.placeholder=""}
	input.onblur = ()=>{input.placeholder=0}
	return input
}
function amount_click_neutral(div,amount,input){
	div.onclick = ()=>{
		input.value = amount
		transfer_info({"target":input})
	}
}
function amount_click_ship(div,amount,input){
	div.onclick = ()=>{
		var space_used = 0
		Object.entries(transfer.sell).forEach(e=>{
			var item = e[0]
			var amount = e[1]
			var size = idata[item].size
			space_used += size*amount
		})
		input.value = Math.max(Math.min(structure.inventory.space_left-space_used,amount),0)
		transfer_info({"target":input})
	}
}
function amount_click_structure(div,amount,input){
	div.onclick = ()=>{
		var space_used = 0
		Object.entries(transfer.buy).forEach(e=>{
			var item = e[0]
			var amount = e[1]
			var size = idata[item].size
			space_used += size*amount
		})
		input.value = Math.max(Math.min(pship.inventory.space_left-space_used,amount),0)
		transfer_info({"target":input})
	}
}

function make_list(name){
	var inputs = Array.from(document.getElementsByClassName(name))
	var list = inputs.map(b=>Math.floor(Number(b.value))>0?{[b.item]:Math.floor(Number(b.value))}:null).filter(b=>b)
	return Object.assign({},...list)
}
function do_transfer(){
	var unpack = window.unpack_ships.checked
	var table = {
		data: [
			{
				action: unpack ? "buy-ship" : "buy",
				self: pship.name,
				other: structure.name,
				items: transfer.buy
			},
			{
				action: "sell",
				self: pship.name,
				other: structure.name,
				sgear: false,
				items: transfer.sell
			}
		]
	}
	if(!unpack){
		table.data[0].sgear = false
	}
	send("transfer",table)
}
function do_transfer2(){
	var table = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: make_list("item_ship")
			},
			{
				action: "take",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: make_list("item_station")
			},
			{
				action: "give",
				self: pship.name,
				other: structure.name,
				sgear: true,
				ogear: true,
				items: make_list("item_shipgear")
			},
			{
				action: "take",
				self: pship.name,
				other: structure.name,
				sgear: true,
				ogear: true,
				items: make_list("item_stationgear")
			}
		]
	}
	send("transfer",table)
}
function do_give_credits(){
	var give = Math.floor(Number(window.give_credits.value))
	give && send("give-credits",{"amount":give})
	window.give_credits.value = 0
}
function do_take_credits(){
	var take = Math.floor(Number(window.take_credits.value))
	take && send("take-credits",{"amount":take})
	window.take_credits.value = 0
}
function do_sellall(){
	var sell = {}
	for(let [item,amount] of Object.entries(items)){
		if(itypes[active_tradetab].includes(item)){
			sell[item] = amount
		}
	}
	var table = {
		data: [
			{
				action: "sell",
				self: pship.name,
				other: structure.name,
				sgear: false,
				items: sell
			}
		]
	}
	send("transfer",table)
}
function do_equip(){
	var table = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: pship.name,
				sgear: false,
				ogear: true,
				items: make_list("off")
			},
			{
				action: "take",
				self: pship.name,
				other: pship.name,
				sgear: false,
				ogear: true,
				items: make_list("on")
			}
		]
	}
	send("transfer",table)
}
function do_equip2(){
	var table = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: pship.name,
				sgear: false,
				ogear: true,
				items: make_list("item_ship")
			},
			{
				action: "take",
				self: pship.name,
				other: pship.name,
				sgear: false,
				ogear: true,
				items: make_list("item_shipgear")
			},
			{
				action: "give",
				self: structure.name,
				other: structure.name,
				sgear: false,
				ogear: true,
				items: make_list("item_station")
			},
			{
				action: "take",
				self: structure.name,
				other: structure.name,
				sgear: false,
				ogear: true,
				items: make_list("item_stationgear")
			}
		]
	}
	send("transfer",table)
}
function do_storeall(){
	var table = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: items
			}
		]
	}
	send("transfer",table)
}
function do_takeall(){
	var table = {
		data: [
			{
				action: "take",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: structure.inventory.items
			}
		]
	}
	send("transfer",table)
}
function do_equip_blueprint(){
	if(selected_blueprint){
		send("equip-blueprint",{"blueprint":selected_blueprint})
	}
}
function do_repair_hull(){
	var stats = selected_ship.stats
	var amount = Number(window.repair_hull_amount.value)
	send("repair",{"ship":selected_ship.name,"hull":amount,"armor":0})
}
function do_repair_armor(){
	var stats = selected_ship.stats
	var amount = Number(window.repair_armor_amount.value)
	send("repair",{"ship":selected_ship.name,"hull":0,"armor":amount})
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

// testing in console
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
window.transfer_credits_give.onclick = do_give_credits
window.transfer_credits_take.onclick = do_take_credits
window.sell_all.onclick = do_sellall
window.store_all.onclick = do_storeall
window.take_all.onclick = do_takeall
window.equip.onclick = do_equip
window.equip2.onclick = do_equip2
window.equip_blueprint.onclick = do_equip_blueprint
window.repair_hull_amount.onblur = update_repair2
window.repair_armor_amount.onblur = update_repair2
window.repair_hull.onclick = do_repair_hull
window.repair_armor.onclick = do_repair_armor
window.trade_setup_add_row.onclick = window.trade_setup.add_row
window.give_credits.onblur = f.only_numbers
window.take_credits.onblur = f.only_numbers
window.update_trade_prices.onclick = do_update_trade_prices

send("get-goods")
