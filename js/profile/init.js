var f=func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

// msg variables
var msg = {}

var first_message = true
function send(command,table={},testing=false){
	table.key = key
	table.command = command
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
			update_achievements(msg)
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

function update_achievements(msg){
	var ach = msg.achievements
	var {discovered,visited,killed} = ach
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
	msg.skills.forEach((k,v)=>{
		var txt = v.name+": "+v.current
		var div = f.addElement(window.list_skills,"div",txt)
	})
	window.int_rep.innerHTML = "Reputation: "+f.formatNumber(msg.reputation)
	window.list_net_worth.innerHTML = "Net worth: "
	var net_worth_types = {
		"total": "Total",
		"credits": "Credits",
		"ships": "Ships",
		"items_ship": "Items in ships",
		"stations": "Stations",
		"items_station": "Items in stations",
		"credits_station": "Credits in stations"
	}
	net_worth_types.forEach((k,v)=>{
		window.list_net_worth.innerHTML += "<br>"+v+": "+f.formatNumber(msg.net_worth[k])
	})
	window.list_quests_completed.innerHTML = "Quests completed: "+Object.keys(msg.cdata.quests_completed||{}).length
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
	window.int_pop_total.innerHTML = "Total population: "+pop_total
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

send("get-profile")
