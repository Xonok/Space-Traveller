/*
CODE STATUS - messy
*Many things should be split off into their own files.
*Table code needs to use standard functions, like some aldready do.
*Stations on the tile should be in hot ships near you, with a dock button.
However, server-side support is not there, so for now the dock button would work exactly like the navbar one.
*/

var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var pship
var pships
var cdata
var quests
var position = [0,0]
var structure = {}
var hwr = {}
var characters = {}

var hwr_timer
var prev_msg
var prev_msg_count = 0
var prev_error
var prev_error_count = 0
var move_delay_timer
var last_action_time = Date.now()
function send(command,table={}){
	table.key = key
	table.command = command
	if(pship && !table.ship){
		table.ship = pship.name
	}
	var char = sessionStorage.getItem("char")
	if(char && !table.char){
		table.char = char
	}
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	var send_time = Date.now()/1000
	last_action_time = Date.now()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		var recv_time = Date.now()/1000
		var ping = recv_time-send_time
		if(e.target.status===200){
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url
				return
			}
			window.onkeydown = keyboard_move
			window.error_display.innerHTML = ""
			Array.from(document.getElementsByTagName("td")).forEach(e=>{
				e.style.backgroundColor = null
				if(e.coord_x !== 0 || e.coord_y !== 0){
					e.innerHTML = ""
				}
			})
			var msg = JSON.parse(e.target.response)
			query.receive(msg)
			console.log(msg)
			cdata = msg.cdata
			pship = msg.ships[cdata.ship]
			pships = msg.ships
			quests=cdata.quests
			if(!sessionStorage.getItem("char")){
				sessionStorage.setItem("char",cdata["name"])
			}
			var local_ship = localStorage.getItem("ship")
			if(local_ship){
				if(Object.keys(pships).includes(local_ship)){
					pship = msg.ships[local_ship]
				}
				else{
					localStorage.setItem("ship",pship.name)
				}
			}
			structure = msg["structure"]
			hwr = msg["hwr"]
			characters = msg["characters"]
			var msg_txt = ""
			msg.messages.forEach((m,mID)=>{
				msg_txt += f.formatString(m)
				if(mID+1 < msg.messages.length){
					msg_txt += "<br>"
				}
			})
			if(!msg_txt){
				prev_msg_count = 0
				prev_msg = undefined
			}
			else if(msg_txt === prev_msg){
				prev_msg_count++
				window.info_display.innerHTML = msg_txt+"("+prev_msg_count+")"
			}
			else{
				window.info_display.innerHTML = msg_txt
				prev_msg_count = 1
			}
			prev_msg = msg_txt
			
			update_starmap(msg)
			update_speed()
			if(Object.keys(hwr).length && Object.entries(cdata.quests_completed || {}).length >= 1){
				var worst
				Object.entries(hwr).forEach(e=>{
					var ship_name = e[0]
					var data = e[1]
					if(!worst || worst.seconds < data.seconds){
						worst = data
						worst.name = f.shipName(pships[ship_name],"character")
					}
				})
				window.hwr_name.innerHTML = "Homeworld: "+cdata.home
				window.hwr_charges.innerHTML = "Charges: "+worst.charges+"/"+worst.max_charges
				
				var time_left = ""
				time_left += worst.seconds >= 3600 ? Math.floor(worst.seconds/3600)+"h" : ""
				time_left += worst.seconds >= 60 ? Math.floor(worst.seconds/60)%60+"m" : ""
				time_left += Math.floor(worst.seconds)%60+"s"
				var hwr_status = worst.charges ? "Status: Ready" : "Status: ready in "+time_left
				hwr_status = worst.seconds === -1 ? "Status: "+worst.time_left : hwr_status
				window.hwr_status.innerHTML = hwr_status
				
				if(hwr_timer){
					clearTimeout(hwr_timer)
				}
				var seconds = worst.seconds
				if(worst.seconds !== -1){
					hwr_timer = setInterval(e=>{
						seconds--
						var time_left = ""
						time_left += seconds >= 3600 ? Math.floor(seconds/3600)+"h" : ""
						time_left += seconds >= 60 ? Math.floor(seconds/60)%60+"m" : ""
						time_left += Math.floor(seconds)%60+"s"
						
						if(seconds < 0){
							window.hwr_status.innerHTM = "Status: Ready"
							f.forClass("info_display",e=>{e.innerHTML = "<br>"+"Next tick in: now."})
							clearTimeout(hwr_timer)
						}
						else{
							if(worst.charges){
								window.hwr_status.innerHTML = "Status: "+time_left
							}
							else{
								window.hwr_status.innerHTML = "Status: ready in "+time_left
							}
						}
						
					},1000)
				}
				window.hwr_box.style.display = "flex"
			}
			else{
				window.hwr_box.style.display = "none"
			}
			var {x,y,rotation} = pship.pos
			window.credit.innerHTML= "Credits: "+func.formatNumber(cdata.credits)
			var noun_constellation = config.rainbow ? "Neighbourhood: " : "Constellation: "
			window.constellation.innerHTML = noun_constellation + q.constellation
			var noun_system = config.rainbow ? "Star: " : "System: "
			window.place.innerHTML = noun_system + pship.pos.system
			var noun_coords = config.rainbow ? "GPS: " : "Coordinates: "
			window.player_position.innerHTML = noun_coords + pship.pos.x + "," + pship.pos.y
			var noun_terrain = config.rainbow ? "Land: " : "Terrain: "
			window.tile_terrain.innerHTML = noun_terrain+q.tile.terrain
			var noun_resource = config.rainbow ? "Shinies: " : "Resource: "
			if(q.tile.resource){
				window.tile_resource_text.innerHTML = noun_resource+q.idata[q.tile.resource]["name"]+"("+q.tile.resource_amount+")"
				window.tile_resource_img.setAttribute("src",q.idata[q.tile.resource].img)
			}
			else{
				window.tile_resource_text.innerHTML = noun_resource+"none"
				window.tile_resource_img.removeAttribute("src")
			}
			var noun_structure = config.rainbow ? "House: " : "Structure: "
			if(msg["structure"].ship || msg["structure"].type){
				window.tile_structure.innerHTML = msg["structure"].ship ? noun_structure + msg["structure"].ship : noun_structure + msg["structure"].type
			}
			else{
				window.tile_structure.innerHTML = noun_structure+"none"
			}
			nav.ship.update_ships()
			update_quests(quests)
			console.log(cdata)
			position = [x,y]
			nav.map.update(x,y)
			update_inventory()
			//buttons
			var buttons_visible = false
			for(let [btn,display] of Object.entries(msg.buttons)){
				if(display!=="none"){buttons_visible = true}
				window[btn].style = "display:"+display
			}
			window.actions_empty.style.display = buttons_visible ? "none" : ""
			
			if(move_delay_timer){
				clearInterval(move_delay_timer)
				move_delay_timer = null
			}
			move_delay_timer = setInterval(()=>{
				var time_left = send_time-Date.now()/1000+msg.delay-ping/2
				window.move_timer.innerHTML = "Recharging engines: "+Math.floor(time_left*100)/100
				if(time_left < 0){
					window.move_timer.innerHTML = ""
					clearInterval(move_delay_timer)
					move_delay_timer = null
				}
			},100)
			nav.map.resize()
			prev_error_count = 0
			prev_error = undefined
		}
		else if(e.target.status===400 || e.target.status===500){
			window.info_display.innerHTML = ""
			var err = e.target.response
			if(!err){
				prev_error_count = 0
				prev_error = undefined
			}
			else if(err === prev_error){
				prev_error_count++
				window.error_display.innerHTML = err+"("+prev_error_count+")"
			}
			else{
				window.error_display.innerHTML = err
				prev_error_count = 1
			}
			prev_error = err
			console.log(err)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function update_quests(quests){
	window.questlines.innerHTML=""
	if(!Object.entries(quests).length){
		window.questlines.innerHTML="<it>No quests active currently.</it>"
		window.questlines.style="color:lightblue;"
	}
	else{
		for (const [questname, info] of Object.entries(quests)) {
		window.questlines.innerHTML+=questname+"</br>"
		}
	}
}
function update_starmap(msg){
	window.starmap.innerHTML = ""
	var sm = msg.starmap
	var make_anchor = (txt)=>{
		if(txt){
			var el = document.createElement("a")
			el.href = "/map.html?star="+txt
			el.innerHTML = txt
			return el
		}
		return ""
	}
	if(!sm){
		f.row(window.starmap,"","","")
		f.row(window.starmap,"","???","")
		f.row(window.starmap,"","","")
		return
	}
	f.row(window.starmap,make_anchor(sm.nw),make_anchor(sm.n),make_anchor(sm.ne))
	f.row(window.starmap,make_anchor(sm.w),make_anchor(pship.pos.system),make_anchor(sm.e))
	f.row(window.starmap,make_anchor(sm.sw),make_anchor(sm.s),make_anchor(sm.se))
}
function update_speed(){
	var spd = nav.fleet.speed()
	var clean = s=>Math.round(s*10)/10
	var mod = terrain[q.tile.terrain].move_cost
	window.fleet_speed.innerHTML = "Speed: "+clean(spd/mod)
	var slowest_ship
	var slowest_speed = 100000
	Object.values(pships).forEach(pship=>{
		if(pship.stats.speed < slowest_speed){
			slowest_ship = pship.custom_name ? pship.custom_name+","+pship.id : pship.name
			slowest_speed = pship.stats.speed
		}
	})
	var tt = f.addElement(window.fleet_speed,"span","Fleet speed: "+clean(spd)+"<br>Terrain modifier: "+mod+"<br>Slowest ship: "+slowest_ship+" ("+clean(slowest_speed)+")")
	tt.className = "tooltiptext"
}
function openTab(e,name){
	var tabcontent = document.getElementsByClassName("tabcontent")
	for(let i = 0; i < tabcontent.length; i++){
		tabcontent[i].style.display = "none"
	}
	var tablinks = document.getElementsByClassName("tablinks")
	for(let i = 0; i < tablinks.length; i++){
		tablinks[i].className = tablinks[i].className.replace(" active", "")
	}
	document.getElementById(name).style.display = "flex"
	e.currentTarget.className += " active"
}

window.space_map.onclick = do_move
var ready = f=>["complete","interactive"].includes(document.readyState) ? f() : document.addEventListener("DOMContentLoaded",f)

ready(()=>{
	if(!nav.map){console.log("nav.map not loaded early enough.")}
	nav.map.init(window.space_map)
	send("get-location")
})
// right click
// var notepad = document.getElementById("notepad");
// notepad.addEventListener("contextmenu",function(event){
    // event.preventDefault();
    // var ctxMenu = document.getElementById("ctxMenu");
    // ctxMenu.style.display = "block";
    // ctxMenu.style.left = (event.pageX - 10)+"px";
    // ctxMenu.style.top = (event.pageY - 10)+"px";
// },false);
// notepad.addEventListener("click",function(event){
    // var ctxMenu = document.getElementById("ctxMenu");
    // ctxMenu.style.display = "";
    // ctxMenu.style.left = "";
    // ctxMenu.style.top = "";
// },false);
