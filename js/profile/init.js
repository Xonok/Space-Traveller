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
	killed.forEach((k,v)=>{
		var box = f.addElement(window.list_killed,"div")
		var blah = f.addElement(box,"div")
		
		var options = {
			year: "numeric",
			month: "short",
			day: "numeric",
		}
		blah.innerHTML += v.name+": "+v.amount
		blah.innerHTML += " (first: "+new Date(v.time_first*1000).toLocaleString(undefined, options)+")"
		//blah.innerHTML += "<br>Last: "+new Date(v.time_last*1000).toLocaleString(undefined, options)
		// console.log(k,v)
	})
	if(!Object.entries(killed).length){
		window.list_killed.innerHTML = "None"
	}
	window.name_character.innerHTML = "Character: "+msg.cdata.name
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
}

send("get-profile")
