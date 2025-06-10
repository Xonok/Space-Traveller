/*CODE STATUS - messy
*Many things should be split off.
*UI and logic code are sometimes mixed.
*Many many table functions that do essentially the same thing.
Using the table system that nav uses would be better, but it's currently not ready.
*/

var active_docktab
function open_tab(e) {
	if(e.target.style.display==="none"){return}
	var name = e.target.getAttribute("name")
	if(active_docktab){window[active_docktab].style.display="none"}
	active_docktab = name
	window[active_docktab].style.display="flex"
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
	window[active_docktab].style.display="flex"
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
var tabs_with_subtabs=["Trade", "Ship","Manage","Station"]
function docktab_design(){
	window.tradetabs.style.display=active_docktab==="Trade"?"block":"none"
	window.divider4.style.display=tabs_with_subtabs.includes(active_docktab)?"none":"initial"
	window.divider5.style.display=tabs_with_subtabs.includes(active_docktab)?"none":"initial"
	window.divider5_duplicate.style.display=tabs_with_subtabs.includes(active_docktab)?"block":"none"
	if(active_docktab==="Station"){
		window.station_owner.innerHTML="Owner: "+q.structure.owner
	}
}
f.forClass("docktab",e=>e.onclick = open_tab)

function update(){
	update_tables()
	update_labels()
	update_manage()
	update_ship_list()
	update_repair()
	update_tabs()
	dock_update_quests()
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
function update_tables(){
	update_trade_tables()
	update_ship_tables()
	update_items_tables()
	update_station_tables()
}
function update_messages(){
	window.info_display.innerHTML = ""
	q.messages.forEach((m,mID)=>{
		window.info_display.innerHTML += m
		if(mID+1 < q.messages.length){
			window.info_display.innerHTML += "<br>"
		}
	})
}	
function update_labels(){
	// trade, repair, items
	f.forClass("ship_credits",e=>e.innerHTML = "Credits: "+f.formatNumber(q.cdata.credits))
	// trade and items
	f.forClass("structure_credits",e=>e.innerHTML = "Credits: "+f.formatNumber(q.structure.credits))
	//trade, station, items
	f.forClass("structure_room",e=>e.innerHTML = "Room left: "+f.formatNumber(q.structure.stats.room.current)+"/"+f.formatNumber(q.structure.stats.room.max))
	// trade, ship, items
	var room_left_all = q.cdata.stats.room.current
	var room_max_all = q.cdata.stats.room.max
	f.forClass("ship_room",e=>e.innerHTML = "Room left: "+f.formatNumber(q.pship.stats.room.current)+"/"+f.formatNumber(q.pship.stats.room.max))
	f.forClass("ship_room2",e=>e.innerHTML = "Room left: "+f.formatNumber(room_left_all)+"/"+f.formatNumber(room_max_all))
	// dock info
	var name = q.structure.custom_name || q.structure.name
	window.structure_name.innerHTML = name+"<br>"+q.idata[q.structure.ship].name
}

// shipdiv
var selected_ship_btn
var selected_ship
function update_ship_list(){
	window.ship_list.innerHTML = ""
	window.twitter.innerHTML = ""
	// same if condition after loop
	if(!selected_ship || !q.pships[selected_ship.name]){
		selected_ship = q.pship
	}
	Object.values(q.pships).forEach(s=>{
		var ship_list
		if(q.cdata.ships.includes(s.name)){
			ship_list = window.ship_list
		}
		else{
			ship_list = window.twitter
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
			if(selected_ship !== q.pship){
				q.pship = s
				localStorage.setItem("ship",s.name)
				update()
				update_repair(true)
			}
			window.dock_ship_name.innerHTML = "Ship: " + f.shipName(s,"character")
			
		}
		if(selected_ship && selected_ship.name === s.name){
			btn.click()
		}
	})
	if(!selected_ship || q.pships[selected_ship.name] !== selected_ship){
		window.ship_list.childNodes[0].click()
	}
	window.storage_img.src = q.idata[q.structure.ship].img
}

function update_tabs(){
	var module_slots = q.idata[q.structure.ship].slots.module || 0
	var first_possible_tab
	var possible_tabs = []
	f.forClass("docktab",(t)=>{
		t.style.display = "block"
		var display = (name,check)=>{
			if(t.innerHTML !== name){return}
			t.style.display = check ? "block" : "none"
		}
		display("Planet(P)",q.structure.type === "planet")
		display("Quests(Q)",q.structure.type === "planet")
		display("Trade(T)",Object.keys(q.prices).length)
		display("Manage(M)",q.structure.owner === q.cdata.name)
		display("Population(P)",q.structure.industries?.length)
		display("Station(B)",q.structure.owner === q.cdata.name)
		display("Construction(C)",q.structure.owner === q.cdata.name && module_slots)
		display("Transport(T)",q.structure.owner === q.cdata.name)
		display("Neuro-Training(N)",Object.keys(q.skill_location||{}).length)
		if(t.style.display !== "none" && !first_possible_tab){
			first_possible_tab = t
		}
		if(t.style.display !== "none"){
			possible_tabs.push(t.getAttribute("name"))
		}
	})
	var local_tab = localStorage.getItem("tab_active")
	if(local_tab && active_docktab !== local_tab){
		open_tab_by_name(local_tab)
	}
	if((!active_docktab || !possible_tabs.includes(active_docktab)) && first_possible_tab){
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
		f.send("get-goods",{},true)
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
function dock_keydown(e){
	if(e.repeat || e.shiftKey || e.ctrlKey){return}
	if(e.code === "Enter" && document.activeElement.nodeName === "INPUT"){
		e.target.blur()
		return
	}
	var name = document.activeElement.nodeName
	if(["INPUT","TEXTAREA"].includes(name)){return}
	if(e.code==="Escape"){f.view.open("nav")}
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

var quest_ended = false
function dock_open(){
	if(q.tile && !q.tile?.structure){
		f.view.open("nav")
		return
	}
	f.send("get-goods")
}
function dock_message(msg){
	if(!q.tile?.structure){
		f.view.open("nav")
		return
	}
	make_tradetab_buttons()
	if(msg.quest_end_text){
		quest_ended = true
		end_quest()
	}
	else{
		quest_ended = false
	}
	update()
}
f.view.register("dock",dock_open,dock_message,dock_keydown)
