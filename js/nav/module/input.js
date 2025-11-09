function do_move(e){
	if(!nav.map){console.log("ignoring move, map not loaded yet");return}
	if(e.target.nodeName !== "CANVAS"){return}
	var canvas = e.target
	var rect = canvas.getBoundingClientRect()
	var canvas_mouse_x = e.clientX - rect.left
	var canvas_mouse_y = e.clientY - rect.top
	var [x,y] = position
	var cell_coord_x = Math.floor((canvas_mouse_x)/nav.map.cell_width)-q.vision
	var cell_coord_y = Math.floor((canvas_mouse_y)/nav.map.cell_width)-q.vision
	var x2 = x+cell_coord_x
	var y2 = y-cell_coord_y	
	if(cell_coord_x === 0 && cell_coord_y === 0){
		interact()
	}
	else{
		f.send("move",{"tx":x2,"ty":y2})
	}
}
function do_move_rel(dx,dy){
	f.send("move-relative",{dx,dy})
}
function do_dock(){
	f.view.open("dock")
}
function interact(){
	if(q.tile.jump_target){
		do_jump()
	}
	else if(q.map_structure.name){
		do_dock()
	}
	else if(attack_target){
		do_start_battle()
	}
	else{
		do_gather()
	}
}
function do_start_battle(){
	if(!attack_target){
		return
	}
	f.send("start-battle",{"target":attack_target})
}
var do_gather = ()=>f.send("gather")
function do_mine(){
	if(!q.tile.landmark?.props.resources){return}
	var resources = Array.from(Object.keys(q.tile.landmark.props.resources))
	if(!resources.length){return}
	var resource = resources[0]
	f.send("mine",{"target":q.tile.landmark.id,resource})
}
var do_excavate = ()=>f.send("excavate",{"struct_name":q.map_structure.name})
var do_investigate = ()=>f.send("investigate",{"struct_name":q.map_structure.name})
var do_loot_all = ()=>{
	var table = window.inv_loot_loot.table
	var data = table.get_values("amount",Number)
	f.send("take-loot",{"take_items":data})
}
var do_loot = (i)=>f.send("take-loot",{"take_items":i})
var do_jump = ()=>{
	nav.map.x = undefined
	nav.map.y = undefined
	nav.map.r = undefined
	f.send("jump")
}
var do_pack = ()=>f.send("pack-station")
var do_dropall = ()=>f.send("drop",{"drop_items":q.cdata.items})
var do_drop = (i)=>{f.send("drop",{"drop_items":i});console.log(i)}
var do_hwr = ()=>f.send("homeworld-return")
var do_rename = ()=>{
	f.send("ship-rename",{"name":window.ship_name.value})
}
var last_action_time = Date.now()
function nav_keydown(e){
	if(e.shiftKey || e.ctrlKey){return}
	var now = Date.now()
	if(e.repeat && (now-last_action_time < 200 || move_delay_timer)){
		e.preventDefault()
		return
	}
	last_action_time = now
	if(e.code === "Enter" && document.activeElement.nodeName === "INPUT"){
		e.target.blur()
		return
	}
	var name = document.activeElement.nodeName
	if(["INPUT","TEXTAREA"].includes(name)){return}
	var right=["KeyD","Numpad6","ArrowRight"].includes(e.code)
	var left=["KeyA","Numpad4","ArrowLeft"].includes(e.code)
	var up=["KeyW","Numpad8","ArrowUp"].includes(e.code)
	var down=["KeyS","Numpad2","ArrowDown"].includes(e.code)
	if(left){do_move_rel(-1,0)}
	else if(right){do_move_rel(1,0)}
	else if(up){do_move_rel(0,1)}
	else if(down){do_move_rel(0,-1)}
	else if(e.code==="KeyG"){do_gather()}
	else if(e.code==="KeyM"){do_mine()}
	else if(e.code==="KeyI"){do_investigate()}
	else if(e.code==="KeyT"){do_dock()}
	else if(e.code==="KeyK"){do_start_battle()}
	else if(e.code==="KeyL"){do_loot_all()}
	else if(e.code==="KeyJ"){do_jump()}
	else if(e.code==="Enter"){interact()}
	else if(e.code==="KeyE"){do_excavate()}
	else if(e.code==="Numpad5"){interact()}
	else if(e.code==="Space"){interact()}
	else if(e.code.includes("Digit")){
		var nr = Number(e.code.substring(5,6))
		if(nr <= usable_items.length){
			f.send("use-item",{"item":usable_items[nr-1]})
		}
	}
	// diagonals
	else if(e.code==="Numpad9"){do_move_rel(1,1)}
	else if(e.code==="Numpad3"){do_move_rel(1,-1)}
	else if(e.code==="Numpad7"){do_move_rel(-1,1)}
	else if(e.code==="Numpad1"){do_move_rel(-1,-1)}
	else{return}
	e.preventDefault()
}

window.gather.onclick = do_gather
window.excavate.onclick = do_excavate
window.investigate.onclick = do_investigate
window.loot_all.onclick = do_loot_all
window.pack.onclick = do_pack
window.drop_all.onclick = do_dropall
window.hwr_btn.onclick = do_hwr
window.ship_name.onfocus = e=>{
	e.target.value = q.pship.custom_name || ""
}
window.ship_name.onblur = do_rename
window.ship_name.onkeydown = e=>{
	if(e.code === "Enter"){
		e.target.blur()
		e.stopPropagation()
		e.preventDefault()
	}
}