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
	if(e.target.style.display==="none"){return}
	var name = e.target.getAttribute("name")
	if(active_docktab){window[active_docktab].style.display="none"}
	active_docktab = name
	window[active_docktab].style.display="block"
	docktab_design()
	f.forClass("docktab",el=>{
		el.className = el.className.replace(" active", "")
	})
	e.target.className += " active"
	localStorage.setItem("tab_active",name)
}
function open_tab_by_name(name){
	var target
	f.forClass("docktab",el=>{
		if(el.getAttribute("name") === name && el.style.display !== "none"){
			target = el
		}
	})
	if(!target){return}
	if(target.style.display==="none"){return}
	if(active_docktab){window[active_docktab].style.display="none"}
	active_docktab = name
	window[active_docktab].style.display="block"
	docktab_design()
	f.forClass("docktab",el=>{
		el.className = el.className.replace(" active", "")
	})
	target.className += " active"
	localStorage.setItem("tab_active",name)
}
var docktab_message = {
	// "repair_msg": "If you no repair hull, you slow."
}
f.forClass("custom_message_docktabs", div=>div.innerHTML = docktab_message[div.id] || "")
function docktab_design(){
	window.tradetabs.style.display=active_docktab==="Trade"?"block":"none"
	window.divider4.style.display=active_docktab==="Trade"?"none":"initial"
	window.divider5.style.display=active_docktab==="Trade"?"none":"initial"
	window.divider5_duplicate.style.display=active_docktab==="Trade"?"block":"none"
	if(active_docktab==="Station"){
		window.station_owner.innerHTML="Owner: "+structure.owner
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
var transport_targets = {}
var skill_loc = {}
var skill_data = {}
var image_name

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
			window.onkeydown = keyboard_move
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
			transport_targets = msg.transport_targets
			skill_loc = msg.skill_loc
			skill_data = msg.skill_data
			image_name=ship_defs[structure.ship].img 
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

function update(){
	clear_tables()
	update_tables()
	update_labels()
	update_manage()
	update_ship_list()
	update_repair()
	update_tabs()
	update_quests()
	update_pop()
	update_blueprints()
	update_stats()
	update_stats2()
	update_stat_meaning()
	update_transport()
	update_training()
	update_messages()
	update_overview()
}
function clear_tables(){
	Array.from(document.getElementsByTagName("table")).forEach(e=>{
		// is nessesary?
		if(e.id==="construct"){return}
		e.innerHTML = ""
	})
}
function update_tables(){
	update_trade_tables()
	update_ship_tables()
	update_items_tables()
	update_station_tables()
}
function update_messages(){
	window.info_display.innerHTML = ""
	msg.messages.forEach((m,mID)=>{
		window.info_display.innerHTML += m
		if(mID+1 < msg.messages.length){
			window.info_display.innerHTML += "<br>"
		}
	})
}	
function update_labels(){
	// trade, repair, items
	f.forClass("ship_credits",e=>e.innerHTML = "Credits: "+f.formatNumber(cdata.credits))
	// trade and items
	f.forClass("structure_credits",e=>e.innerHTML = "Credits: "+f.formatNumber(structure.credits))
	//trade, station, items
	f.forClass("structure_room",e=>e.innerHTML = "Room left: "+f.formatNumber(sinv.room_left)+"/"+f.formatNumber((sinv.room_max+sinv.room_extra)))
	// trade, ship, items
	var room_left_all = Object.values(pships).map(ps=>ps.inventory.room_left).reduce((a,b)=>a+b,0)
	var room_max_all = Object.values(pships).map(ps=>ps.inventory.room_max+ps.inventory.room_extra).reduce((a,b)=>a+b,0)
	var room_left = window.trade_all_ships.checked ? room_left_all : inv.room_left
	var room_max = window.trade_all_ships.checked ? room_max_all : (inv.room_max+inv.room_extra)
	f.forClass("ship_room",e=>e.innerHTML = "Room left: "+f.formatNumber(pship.inventory.room_left)+"/"+f.formatNumber(pship.inventory.room_max+pship.inventory.room_extra))
	f.forClass("ship_room2",e=>e.innerHTML = "Room left: "+f.formatNumber(room_left)+"/"+f.formatNumber(room_max))
	// dock info
	var name = structure.custom_name || structure.name
	window.structure_name.innerHTML = name+"<br>"+ship_defs[structure.ship].name
	var reputation = structure.props?.reputation?.[cdata.name] || 0
	var rep_text = "Your reputation: "+reputation+"<br>"
	if(structure.type !== "planet"){
		rep_text = ""
	}
	var desc_text = "Owner: "+structure.owner+"<br><br>"+rep_text+(structure.desc || "No description available")
	f.tooltip2(window.structure_name,desc_text)
	window.planet_desc.innerHTML = desc_text
}

// shipdiv
var selected_ship_btn
var selected_ship
function update_ship_list(){
	window.ship_list.innerHTML = ""
	window.twitter.innerHTML = ""
	// same if condition after loop
	if(!selected_ship){
		selected_ship = pship
	}
	Object.values(pships).forEach(s=>{
		if(cdata.ships.includes(s.name)){
			var ship_list = window.ship_list
		}
		else{
			var ship_list = window.twitter
		}
		
		var box = f.addElement(ship_list,"div")
		box.classList.add("horizontal")
		var img_box = f.addElement(box,"div")
		img_box.classList.add("centered")
		img_box.style.minWidth = "25px"
		img_box.style.minHeight = "25px"
		img_box.style.marginLeft = "10px"
		img_box.style.marginRight = "2px"
		var img = f.addElement(img_box,"img")
		img.src = s.img
		img.style.maxWidth = "25px"
		img.style.maxHeight = "25px"
		var btn = f.addElement(box,"button",f.shipName(s,"character"))
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
				update_repair(true)
			}
			window.ship_name.innerHTML = "Ship: " + f.shipName(s,"character")
			
		}
		if(selected_ship && selected_ship.name === s.name){
			btn.click()
		}
	})
	if(!selected_ship){
		window.ship_list.childNodes[0].click()
	}
	window.storage_img.src=image_name
}

function update_tabs(){
	var module_slots = ship_defs[structure.ship].slots.module || 0
	var first_possible_tab
	f.forClass("docktab",(t)=>{
		t.style.display = "block"
		var display = (name,check)=>{
			if(t.innerHTML !== name){return}
			t.style.display = check ? "block" : "none"
		}
		display("Planet(P)",structure.type === "planet")
		display("Quests(Q)",structure.type === "planet")
		display("Trade(T)",Object.keys(iprices).length)
		display("Items(I)",structure.owner === cdata.name)
		display("Manage(M)",structure.owner === cdata.name)
		display("Population(P)",structure.industries?.length)
		display("Station(B)",structure.owner === cdata.name)
		display("Construction(C)",structure.owner === cdata.name && module_slots)
		display("Transport(T)",structure.owner === cdata.name)
		display("Neuro-Training(N)",Object.keys(skill_loc||{}).length)
		if(!active_docktab && t.style.display !== "none" && !first_possible_tab){
			first_possible_tab = t
		}
	})
	var local_tab = localStorage.getItem("tab_active")
	if(local_tab && active_docktab !== local_tab){
		open_tab_by_name(local_tab)
	}
	if(!active_docktab && first_possible_tab){
		first_possible_tab.click()
		window[first_possible_tab.getAttribute("name")].style.display="block"
	}
}

function update_stat_meaning(){
	var e = window.stat_meaning
	e.innerHTML = "Stat meaning:<br>"
	var data = {
		"tech": "What level you need in some skill to equip the item. The particular skill depends on item type. Note: skills not implemented yet, so this does nothing.",
		"room": "Amount of room in the ship, both for inventory and to equip stuff.",
		"weight": "How heavy a given piece of armor is. This controls how much it reduces agility."
	}
	Object.entries(data).forEach(d=>{
		var k = d[0]
		var v = d[1]
		e.innerHTML += "<b>"+k+"</b>"+" - "+v+"<br>"
	})
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

function open_docktab(name){
	f.forClass("docktab",e=>{
		if(e.getAttribute("name") == name){
			e.click()
		}
	})
}
function keyboard_move(e){
	if(e.repeat || e.shiftKey || e.ctrlKey){return}
	if(e.code === "Enter" && document.activeElement.nodeName === "INPUT"){
		e.target.blur()
		return
	}
	var name = document.activeElement.nodeName
	if(["INPUT","TEXTAREA"].includes(name)){return}
	if(e.code==="Escape"){window.location.href = '/nav.html'+window.location.search}
	else if(e.code==="KeyO"){open_docktab("Overview")}
	else if(e.code==="KeyQ"){open_docktab("Quests")}
	else if(e.code==="KeyT"){open_docktab("Trade")}
	else if(e.code==="KeyS"){open_docktab("Ship")}
	else if(e.code==="KeyI"){open_docktab("Items")}
	else if(e.code==="KeyB"){open_docktab("Station")}
	else if(e.code==="KeyM"){open_docktab("Manage")}
	else if(e.code==="KeyC"){open_docktab("Construction")}
	else if(e.code==="KeyP"){open_docktab("Population")}
	else if(e.code==="KeyT"){open_docktab("Transport")}
	else if(e.code==="KeyN"){open_docktab("Neuro_Training")}
	else if(e.code==="Digit1"){/*Switch to first tab*/}
	else{return}
	e.preventDefault()
}

send("get-goods")
