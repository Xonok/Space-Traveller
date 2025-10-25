var pship
var position = [0,0]

var hwr_timer
var prev_msg
var prev_msg_count = 0
var prev_error
var prev_error_count = 0
var move_delay_timer
var last_action_time = Date.now()
function nav_update_quests(){
	window.questlines.innerHTML=""
	if(!Object.entries(q.cdata.quests).length){
		window.questlines.innerHTML="<it>No quests active currently.</it>"
		window.questlines.style="color:lightblue;"
	}
	else{
		for (const [questname, info] of Object.entries(q.cdata.quests)) {
		window.questlines.innerHTML+=questname+"<br>"
		}
	}
}
function update_speed(){
	if(!q.tile){return}
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

function nav_open(){
	window.space_map.onclick = do_move
	if(!nav.map){console.log("nav.map not loaded early enough.")}
	nav.map.init(window.space_map)
	f.send("get-location")
}
function nav_message(msg){
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
	var {x,y} = q.pship.pos
	window.credit.innerHTML = ""
	var credit_img_box = f.img_box(window.credit,"1em","1em","img/credits.webp")
	credit_img_box.style.marginRight = "2px"
	f.addElement(window.credit,"div","Credits: "+func.formatNumber(q.cdata.credits))
	var noun_constellation = config.rainbow ? "Neighbourhood: " : "Constellation: "
	var noun_pos = config.rainbow ? "GPS: " : "Position: "
	window.constellation.innerHTML = noun_constellation + q.constellation
	window.player_position.innerHTML = noun_pos + q.pship.pos.system + "(" + q.pship.pos.x + "," + q.pship.pos.y + ")"
	var pvp_options = {
		"open": "Full"
	}
	window.star_pvp.innerHTML = ""
	var pvp_box = f.addElement(window.star_pvp,"div","PvP:&nbsp")
	pvp_box.classList.add("horizontal")
	var pvp_status = pvp_options[q.star_props.pvp] || "None"
	var pvp_div = f.addElement(pvp_box,"div",pvp_status)
	pvp_div.style.color = q.star_props.pvp === "open" ? "red" : "green"
	var pvp_reasons = q.star_props.pvp === "open" ? "Every single player can attack you here." : "Players can't attack you here."
	f.tooltip2(pvp_div,pvp_reasons)
	var noun_terrain = config.rainbow ? "Land: " : "Terrain: "
	window.tile_terrain.innerHTML = noun_terrain+nav.map.terrain_name[q.tile.terrain]
	window.tile_resource.innerHTML = ""
	var noun_resource = config.rainbow ? "Shinies: " : "Resource: "
	if(q.tile.resource){
		var tile_res_box = f.addElement(window.tile_resource,"div")
		tile_res_box.classList.add("horizontal")
		tile_res_box.innerHTML += noun_resource
		f.img_box(tile_res_box,"1rem","1rem",q.idata[q.tile.resource].img)
		tile_res_box.innerHTML += q.idata[q.tile.resource]["name"]+"("+q.tile.resource_amount+")"
	}
	else{
		window.tile_resource.innerHTML = noun_resource+"none"
	}
	var landmark_resources = q.tile.landmark?.props.resources
	if(landmark_resources){
		var res = Object.keys(landmark_resources)[0]
		var tile_res_box2 = f.addElement(window.tile_resource,"div")
		tile_res_box2.classList.add("horizontal")
		tile_res_box2.innerHTML += "Special: "
		console.log(q.idata[res],res)
		f.img_box(tile_res_box2,"1rem","1rem",q.idata[res].img)
		tile_res_box2.innerHTML += q.idata[res]["name"]+"("+landmark_resources[res]+")"
	}
	nav.ship.update_ships()
	nav_update_quests()
	position = [x,y]
	update_inventory()
	//buttons
	var can_gather = !!q.tile.resource
	var can_mine = !!q.tile.landmark?.props.resources
	var can_excavate = q.map_structure?.excavate === true
	var can_pack = q.map_structure?.owner === q.cdata.name
	var buttons_visible = can_gather || can_excavate || can_pack
	window.gather.style.display = can_gather ? "initial" : "none"
	window.mine.style.display = can_mine ? "initial" : "none"
	window.excavate.style.display = can_excavate ? "initial" : "none"
	window.investigate.style.display = can_excavate ? "initial" : "none"
	window.pack.style.display = can_pack ? "initial" : "none"
	window.actions_empty.style.display = buttons_visible ? "none" : ""
	
	if(msg.delay){
		if(move_delay_timer){
			clearInterval(move_delay_timer)
			move_delay_timer = null
		}
		move_delay_timer = setInterval(()=>{
			var time_left = q.delay-Date.now()/1000+func.time.offset
			window.move_timer.innerHTML = "Recharging engines: "+Math.floor(time_left*100)/100
			if(time_left < 0){
				window.move_timer.innerHTML = ""
				clearInterval(move_delay_timer)
				move_delay_timer = null
			}
		},100)
	}
	if(!nav.map.resize()){
		nav.map.should_draw = true
	}
}
f.view.register("nav",nav_open,nav_message,nav_keydown)
