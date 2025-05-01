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
var position = [0,0]

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
		table.active_ship = pship.name
	}
	var char = sessionStorage.getItem("char")
	if(char && !table.active_character){
		table.active_character = char
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
			document.title = "Space Traveller: "+q.cdata.name
			pship = q.pships[q.cdata.ship]
			if(!sessionStorage.getItem("char")){
				sessionStorage.setItem("char",q.cdata["name"])
			}
			var local_ship = localStorage.getItem("ship")
			if(local_ship){
				if(Object.keys(q.pships).includes(local_ship)){
					pship = q.pships[local_ship]
				}
				else{
					localStorage.setItem("ship",pship.name)
				}
			}
			var msg_txt = ""
			q.messages.forEach((m,mID)=>{
				msg_txt += f.formatString(m)
				if(mID+1 < q.messages.length){
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
			
			update_starmap()
			update_speed()
			if(Object.keys(q.hwr).length && Object.entries(q.cdata.quests_completed || {}).length >= 1){
				var worst
				Object.entries(q.hwr).forEach(e=>{
					var ship_name = e[0]
					var data = e[1]
					if(!worst || worst.seconds < data.seconds){
						worst = data
						worst.name = f.shipName(q.pships[ship_name],"character")
					}
				})
				window.hwr_name.innerHTML = "Homeworld: "+q.cdata.home
				
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
			var {x,y} = pship.pos
			window.credit.innerHTML = ""
			var credit_img_box = f.img_box(window.credit,"1em","1em","img/credits.webp")
			credit_img_box.style.marginRight = "2px"
			f.addElement(window.credit,"div","Credits: "+func.formatNumber(q.cdata.credits))
			var noun_constellation = config.rainbow ? "Neighbourhood: " : "Constellation: "
			var noun_pos = config.rainbow ? "GPS: " : "Position: "
			window.constellation.innerHTML = noun_constellation + q.constellation
			window.player_position.innerHTML = noun_pos + pship.pos.system + "(" + pship.pos.x + "," + pship.pos.y + ")"
			var noun_terrain = config.rainbow ? "Land: " : "Terrain: "
			window.tile_terrain.innerHTML = noun_terrain+nav.map.terrain_name[q.tile.terrain]
			var noun_resource = config.rainbow ? "Shinies: " : "Resource: "
			if(q.tile.resource){
				window.tile_resource_text.innerHTML = noun_resource+q.idata[q.tile.resource]["name"]+"("+q.tile.resource_amount+")"
				window.tile_resource_img.setAttribute("src",q.idata[q.tile.resource].img)
			}
			else{
				window.tile_resource_text.innerHTML = noun_resource+"none"
				window.tile_resource_img.removeAttribute("src")
			}
			nav.ship.update_ships()
			update_quests()
			console.log(q.cdata)
			position = [x,y]
			update_inventory()
			//buttons
			var buttons_visible = false
			for(let [btn,display] of Object.entries(q.buttons)){
				if(display!=="none"){buttons_visible = true}
				window[btn].style = "display:"+display
			}
			window.actions_empty.style.display = buttons_visible ? "none" : ""
			
			if(msg.delay){
				if(move_delay_timer){
					clearInterval(move_delay_timer)
					move_delay_timer = null
				}
				move_delay_timer = setInterval(()=>{
					var time_left = send_time-Date.now()/1000+q.delay-ping/2
					window.move_timer.innerHTML = "Recharging engines: "+Math.floor(time_left*100)/100
					if(time_left < 0){
						window.move_timer.innerHTML = ""
						clearInterval(move_delay_timer)
						move_delay_timer = null
					}
				},100)
			}
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
function update_quests(){
	window.questlines.innerHTML=""
	if(!Object.entries(q.cdata.quests).length){
		window.questlines.innerHTML="<it>No quests active currently.</it>"
		window.questlines.style="color:lightblue;"
	}
	else{
		for (const [questname, info] of Object.entries(q.cdata.quests)) {
		window.questlines.innerHTML+=questname+"</br>"
		}
	}
}
function update_starmap(){
	window.starmap.innerHTML = ""
	var sm = q.starmap
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
	Object.values(q.pships).forEach(pship=>{
		if(pship.stats.speed < slowest_speed){
			slowest_ship = pship.custom_name ? pship.custom_name+","+pship.id : pship.name
			slowest_speed = pship.stats.speed
		}
	})
	f.tooltip2(window.fleet_speed,"Fleet speed: "+clean(spd)+"<br>Terrain modifier: "+mod+"<br>Slowest ship: "+slowest_ship+" ("+clean(slowest_speed)+")")
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
