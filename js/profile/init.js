function update_achievements(msg){
	var ach = msg.achievements
	var {discovered,visited,killed} = ach
	window.int_discovered.innerHTML = "Discovered "+Object.keys(discovered).length+" stars."
	window.int_visited.innerHTML = "Visited "+Object.keys(visited).length+" planets."
	window.list_killed.innerHTML = ""
	var total_kills = 0
	killed.forEach((k,v)=>{
		var box = f.addElement(window.list_killed,"div")
		box.classList.add("horizontal")
		f.img_box(box,"25px","25px",v.img)
		var blah = f.addElement(box,"div")
		
		var options = {
			year: "numeric",
			month: "short",
			day: "numeric",
		}
		blah.innerHTML += v.name+": "+v.amount
		var tt_txt = " (first: "+new Date(v.time_first*1000).toLocaleString(undefined, options)+")"
		f.tooltip2(blah,tt_txt)
		total_kills += v.amount
	})
	window.int_kills.innerHTML = "Total: "+total_kills
	if(!Object.entries(killed).length){
		window.list_killed.innerHTML = "None"
	}
	window.name_character.innerHTML = "Character: "+msg.cdata.name
	window.time_created.innerHTML = "Character created: "
	var created = new Date(msg.cdata.props.time_created*1000).toLocaleString(undefined,{year: "numeric",month: "short",day: "numeric",})
	window.time_created.innerHTML += msg.cdata.props.time_created ? created  : "in ancient times"
	window.int_level.innerHTML = "Level: "+msg.cdata.level
	window.int_xp.innerHTML = "XP: "+msg.cdata.xp+"/1000"
	window.int_sp.innerHTML = "Skillpoints: "+msg.cdata.skillpoints
	window.list_skills.innerHTML = ""
	msg.skills.forEach((k,v)=>{
		var txt = v.name+": "+v.current
		f.addElement(window.list_skills,"div",txt)
	})
	window.int_rep.innerHTML = "Reputation: "+f.formatNumber(Math.floor(msg.reputation))
	window.list_net_worth.innerHTML = "Net worth: "
	var net_worth_types = {
		"total": "Total",
		"credits": "Credits",
		"ships": "Ships",
		"items_ship": "Items in ships",
		"stations": "Stations",
		"items_station": "Items in stations",
		"credits_station": "Credits in stations",
		"builds_station": "Builds in stations"
	}
	net_worth_types.forEach((k,v)=>{
		window.list_net_worth.innerHTML += "<br>"+v+": "+f.formatNumber(msg.net_worth[k])
	})
	window.list_quests_completed.innerHTML = "Quests completed: "+Object.keys(msg.cdata.quests_completed||{}).length
	window.list_ships_fleet.innerHTML = ""
	window.list_ships_parked.innerHTML = ""
	msg.pships.forEach((k,v)=>{
		var parent = msg.cdata.ships.includes(v.name) ? window.list_ships_fleet : window.list_ships_parked
		var box = f.addElement(parent,"div")
		box.classList.add("horizontal")
		f.img_box(box,"25px","25px",v.img)
		var blah = f.addElement(box,"div")
		var name = f.shipName(v,"character")
		blah.innerHTML += name
		if(!msg.cdata.ships.includes(v.name)){
			blah.innerHTML += " ("+v.pos.system+","+v.pos.x+","+v.pos.y+")"
		}
	})
	var system_structures = {}
	var pop_total = 0
	msg.structures.forEach((k,v)=>{
		if(!system_structures[v.pos.system]){
			system_structures[v.pos.system] = []
		}
		system_structures[v.pos.system].push(v)
		v.industries.forEach(i=>{
			pop_total += i.workers
		})
	})
	window.int_pop_total.innerHTML = "Total population: "+f.formatNumber(pop_total)
	system_structures.forEach((k,v)=>{
		var system_box = f.addElement(window.list_structures,"div")
		system_box.innerHTML += k
		system_box.style.marginBottom = "5px"
		v.forEach(tstruct=>{
			var box = f.addElement(system_box,"div")
			box.classList.add("horizontal")
			f.img_box(box,"25px","25px",tstruct.img)
			var name = tstruct.custom_name || tstruct.name
			if(tstruct.custom_name){
				name += " ("+tstruct.pos.x+","+tstruct.pos.y+")"
			}
			f.addElement(box,"div",name)
		})
	})
}


function profile_open(){
	f.send("get-profile")
}
function profile_message(msg){
	if(!q.cdata){
		f.view.open("characters")
		return
	}
	update_achievements(msg)
}
f.view.register("profile",profile_open,profile_message)
