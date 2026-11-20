/*
CODE STATUS - outdated and mixed
*Config functions need to be moved from func to config.
*All the table stuff should be in a separate table module, like the one nav uses.
However, the functions here are still being used in Trade, so they can't be removed yet.
*Config shouldn't be in this file.
*Config in general should be moved into a separate folder.
*/

//This check is only needed because utils.load can cause .js files to be loaded twice.
if(typeof func === "undefined"){
	var config = {
		generated: false,
		styles: new CSSStyleSheet(),
		rules: [],
		apply(){
			var add_rule = data=>config.rules.push(config.styles.insertRule(data))
			var family = localStorage.getItem("settings:font")
			if(!family){
				family = "Arial"
			}
			document.adoptedStyleSheets = [config.styles]
			config.rainbow = localStorage.getItem("settings:rainbow_mode")
			config.serious_margin = localStorage.getItem("settings:serious_margin")
			config.grayscale = localStorage.getItem("settings:grayscale")
			
			config.rules.forEach(r=>config.styles.deleteRule(r))
			config.rules = []
			add_rule("*{font-family:"+family+"}")
			config.grayscale && add_rule("html {-moz-filter: grayscale(100%);-webkit-filter: grayscale(100%);filter: gray;filter; grayscale(100%);}")
		}
	}
	if(!config.generated){
		var ctx = {}
		config.apply()
		config.generated = true
	}
	var pagename = window.location.pathname.split("/").pop().split(".")[0]
	func = {
		scripts: [],
		keydown_handlers: {},
		init(views=true){
			if(func.init_done){return}
			func.init_done = true
			html.init_toggles()
			html.init()
			if(views){
				func.view.init()
			}
			else{
				console.log("Views manually disabled.")
			}
			
		},
		send(command,table={},auth=true){
			if(auth){
				var key = localStorage.getItem("key")
				table.key = key
			}
			table.command = command
			if(q.pship !== q.cdata?.ship){
				table.active_ship = q.pship.name
			}
			var char = sessionStorage.getItem("char")
			if(char && !table.active_character){
				table.active_character = char
			}
			table.idata_hash = q.idata_hash
			var send_time = Date.now()/1000
			net.post_json(table,e=>{
				if(e.target.status===200){
					html.forClass("error_display",el=>{
						el.innerHTML = ""
					})
					html.forClass("info_display",el=>{
						el.innerHTML = ""
					})
					var url = e.target.responseURL
					var loc = window.location.pathname
					if(!url.includes(loc)){
						var tokens = url.split("/")
						var view_name = tokens.last().replace(".html","")
						if(f.view.views[view_name]){
							f.view.open(view_name)
							return
						}
						else{
							window.location.href = url
							return
						}
					}
					var msg = JSON.parse(e.target.response)
					func.time.recv(msg,send_time)
					query.receive(msg)
					if(msg.event && msg.event === "page-change"){
						f.view.open(msg.page)
						return
					}
					if(q.cdata){
						document.title = "Space Traveller: "+q.cdata.name
					}
					var msg_txt = ""
					q.messages?.forEach((m,mID)=>{
						msg_txt += f.formatString(m)
						if(mID+1 < q.messages.length){
							msg_txt += "<br>"
						}
					})
					if(!msg_txt){
						func.prev_msg_count = 0
						func.prev_msg = undefined
					}
					else if(msg_txt === func.prev_msg){
						func.prev_msg_count++
						html.forClass("info_display",e=>{
							e.innerHTML = msg_txt+"("+func.prev_msg_count+")"
						})
					}
					else{
						html.forClass("info_display",e=>{
							e.innerHTML = msg_txt
						})
						func.prev_msg_count = 1
					}
					func.prev_msg = msg_txt
					console.log(msg)
					func.view.receive(msg)
					var local_ship = localStorage.getItem("ship")
					if(local_ship && q.pships && Object.keys(q.pships).includes(local_ship)){
						q.pship = q.pships[local_ship]
					}
					if(!err_txt){
						func.prev_err_count = 0
						func.prev_error = undefined
					}
				}
				else if(e.target.status===400 || e.target.status===500){
					var err_txt = e.target.status === 500 ? "Server error." : e.target.response
					if(err_txt === func.prev_error){
						func.prev_err_count++
						html.forClass("error_display",e=>{
							e.innerHTML = err_txt+"("+func.prev_err_count+")"
						})
					}
					else{
						html.forClass("error_display",e=>{
							e.innerHTML = err_txt
						})
						func.prev_err_count = 1
					}
					func.prev_error = err_txt
					console.log(e.target.response)
				}
				else{
					throw new Error("Unknown response status "+e.target.status)
				}
			})
		},
		getSetting(name){
			return localStorage.getItem("settings:"+name)
		},
		setSetting(name,value){
			if(value === null || value === undefined){
				localStorage.removeItem("settings:"+name)
			}
			else{
				localStorage.setItem("settings:"+name,value)
			}
		},
		formatNumber(number){
			var locale = func.getSetting("locale") || navigator.languages
			return number.toLocaleString(locale)
		},
		item_txt(idata){
			var txt = idata.name+"<br><br>"+(idata.desc || "No description available")
			idata.prop_info?.forEach(i=>{
				txt += "<br>"+"&nbsp;".repeat(4)
				txt += i.value !== undefined ? i.key+": "+i.value : i.key
			})
			txt = func.formatString(txt)
			return txt
		},
		tooltip(parent,idata){
			parent.classList.add("tt_parent","dotted")
			var txt = func.item_txt(idata)
			var tt = html.addElement(parent,"span",txt)
			tt.className = "tooltiptext"
			return tt
		},
		tooltip2(parent,txt){
			parent.classList.add("tt_parent","dotted")
			var tt = html.addElement(parent,"div")
			tt.className = "tooltiptext"
			if(Array.isArray(txt)){
				txt.forEach(t=>{
					tt.append(t)
				})
			}
			else{
				tt.innerHTML = func.formatString(txt)
			}
			
			return tt
		},
		tooltip3(parent,div){
			parent.classList.add("tt_parent","dotted")
			parent.append(div)
			div.classList.add("tooltiptext")
		},
		item_tooltip(parent,idata){
			var stats = {
				"general": {
					"tech":"Tech",
					"grade":"Grade",
					"size":"Size",
					"skill": "Skill",
					"skill_req": "Additional skill required",
					"faction": "Faction"
				},
				"general_ship": {
					"tech":"Tech",
					"grade":"Grade",
					"size_item":"Size(item)",
					"size":"Size(ship)",
					"freight": "Freight points",
					"battle": "Battle points",
					"skill": "Skill",
					"faction": "Faction"
				},
				"general_bp": {
					"tech":"Tech",
					"grade":"Grade",
					"skill": "Skill",
					"size":"Size",
					"skill": "Skill",
					"faction": "Faction"
				},
				"general_ship_bp": {
					"tech":"Tech",
					"grade":"Grade",
					"skill": "Skill",
					"size_item":"Size(item)",
					"size":"Size(ship)",
					"freight": "Freight points",
					"battle": "Battle points",
					"skill": "Skill",
					"faction": "Faction"
				},
				"weapon": {
					"type":"Type",
					"mount":"Mount",
					"damage":"Damage",
					"damage_shield": "Damage to shield",
					"damage_armor": "Damage to armor",
					"damage_hull": "Damage to hull",
					"shots":"Shots",
					"shots_pd":"Point Defense",
					"charge":"Reload",
					"preload":"Preload",
					"tracking":"Tracking",
					"targets":"Targets",
					"duration":"Duration",
					"ammo":"Ammo",
					"launch":"Launch"
				},
				"defense": {
					"hull_reg": "Hull repair",
					"armor_max": "Durability",
					"armor_soak": "Protection",
					"armor_reg": "Armor repair",
					"dampen": "Dampening",
					"block": "Block",
					"shield_max": "Max shield",
					"shield_reg":"Regeneration",
					"deflect":"Deflection",
					"stealth": "Stealth"
				},
				"economy": {
					"transport_power": "Transport Power",
					"transport_capacity": "Transport Capacity",
					"mining_power_energy": "Energy mining",
					"mining_power_nebula": "Gas mining",
					"mining_power_asteroids": "Asteroid mining",
					"mining_power_exotic": "Exo mining",
					"mining_power_phase": "Phase mining",
					"mining_bonus_asteroids": "Asteroid mining bonus",
					"mining_efficiency": "Mining efficiency",
					"station_mining": "Allows a station to mine",
					"manual": "Usable",
					"aura_room_bonus": "Extra room",
					"aura_speed_penalty": "Speed penalty",
					"aura_agility_penalty": "Agility penalty",
					"aura_tracking_penalty": "Tracking penalty",
					"aura_speed_bonus": "Speed bonus",
					"room_max": "Extra room",
					"station_mining": "Allows a station to mine",
					"consumable": "Consumable",
					"workers_max_construction": "Maximum construction workers",
					"robots_max_construction": "Maximum construction robots",
					"recycle_max": "Maximum recycling power",
					"recycle_reg": "Recycling power regeneration",
					"workers_max_research": "Maximum research workers",
					"robots_max_research": "Maximum research robots",
					"manual": "Usable",
					"consumable": "consumable",
				},
				"slots": {
					"mining": "Mining",
					"factory": "Factory",
					"sensor": "Sensor",
					"aura": "Aura",
					"farm": "Farm",
					"expander": "Expander",
					"module": "Module",
					"transport": "Transport"
				},
				"slots_battle": {
					"gun": "Gun",
					"missile": "Missile",
					"drone": "Drone",
					"armor": "Armor",
					"shield": "Shield",
				},
				"ship_trade": {
					"room": "Room",
					"room_gear": "Equip",
					"speed": "Speed"
				},
				"ship_battle": {
					"hull": "Hull",
					"agility": "Agility",
					"tracking": "Tracking",
					"control": "Control"
				},
				"station": {
					"hull": "Hull",
					"room": "Room",
					"size": "Size",
					"tracking": "Tracking",
					"control": "Control",
					"tile_limit": "Tile"
				},
				"bonuses": {
					"transport_capacity_mod": "Transport cap mod",
					"transport_power_mod": "Transport power mod",
					"armor_bonus_factor": "Extra armor ratio",
					"shield_bonus_factor": "Extra shield ratio"
				}
			}
			var group_name_override = {
				"general_ship": "general",
				"general_bp": "result",
				"ship_trade": "trade",
				"ship_battle": "battle",
				"slots_battle": "battle slots"
			}
			var create_header = idata=>{
				var box = document.createElement("div")
				box.classList.add("vertical")
				var top_side = html.addElement(box,"div")
				top_side.classList.add("horizontal","tooltip_box")
				var img_box = f.img_box(top_side,5,5,idata.img)
				// img_box.style.marginTop = "2rem"
				img_box.style.marginRight = "5px"
				var desc = html.addElement(top_side,"div",idata.name+"<br><br>"+idata.desc)
				var bot_side = html.addElement(box,"div")
				bot_side.classList.add("horizontal")
				bot_side.style.width = "100%"
				bot_side.style.flexWrap = "wrap"
				return [box,top_side,bot_side]
			}
			var [box,top_side,bot_side] = create_header(idata)
			
			window.seen = window.seen || {name:true,desc:true,img:true}
			var ignored = ["price","amount","limit","prop_info","change","tags","usable","weapon","blueprint","props","faction","slots","ship_predef","name_pluto","img_pluto","img_original","station","input","output","shipdef","factory","bp_category","type"]
			//TODO: slots
			//TODO: names for types
			//TODO: station kits
			var boxes = {}
			var current_parent
			var get_box = (name,itype)=>{
				if(boxes[name]){
					return boxes[name]
				}
				var box = html.addElement(current_parent,"div")
				box.classList.add("tooltip_box")
				box.style.flexGrow = "1"
				box.style.minWidth = "60px"
				box.style.flexBasis = "34%" //Make it so only 2 can fit on line
				box.name = name
				var header_txt = itype||group_name_override[name]||name
				var header = html.addElement(box,"div",header_txt)
				header.style.textAlign = "center"
				boxes[name] = box
				return box
			}
			var box_fill = (group,data,itype)=>{
				if(!data){return}
				var names = stats[group]
				names.forEach((k,v)=>{
					var val = data?.[k]
					if(val !== undefined){
						var box = get_box(group,itype)
						window.seen[k] = true
						box.innerHTML += v+": "+val+"<br>"
					}
				})
			}
			var box_fill_items = (group,data,itype)=>{
				if(!data){return}
				data.forEach((k,v)=>{
					var val = data?.[k]
					if(val !== undefined){
						var box = get_box(group,itype)
						window.seen[k] = true
						box.innerHTML += v+" "+q.idata[k].name+"<br>"
					}
				})
			}
			var itype = idata.type
			var do_item = (idata,is_bp=false)=>{
				var itype = idata.type
				var group_name = itype === "blueprint" ? idata.bp_category+" "+itype : itype
				if(is_bp){
					itype === "ship" ? box_fill("general_ship_bp",idata,group_name) : box_fill("general_bp",idata,group_name)
				}
				else{
					itype === "ship" ? box_fill("general_ship",idata,group_name) : box_fill("general",idata,group_name)
				}
				itype !== "ship" && box_fill("weapon",idata.weapon)
				itype === "ship" && box_fill("slots",idata.slots)
				itype === "ship" && box_fill("slots_battle",idata.slots)
				itype === "ship" && box_fill("ship_trade",idata)
				itype === "ship" && box_fill("ship_battle",idata)
				box_fill("station",idata.shipdef)
				box_fill("station",idata.props)
				box_fill("bonuses",idata.props)
				box_fill("bonuses",idata.shipdef?.props)
				box_fill("slots",idata.shipdef?.slots)
				box_fill("slots_battle",idata.shipdef?.slots)
				box_fill("defense",idata.props)
				box_fill("economy",idata.props)
				box_fill_items("input",idata.factory?.input)
				box_fill_items("output",idata.factory?.output)
				itype === "blueprint" && box_fill_items("recipe",idata.blueprint.inputs)
			}
			current_parent = bot_side
			do_item(idata)
			if(itype === "blueprint"){
				var inner_box = get_box("")
				var [box2,top_side2,bot_side2] = create_header(q.idata[Object.keys(idata.blueprint.outputs)[0]])
				inner_box.append(box2)
				current_parent = bot_side2
				itype === "blueprint" && do_item(q.idata[Object.keys(idata.blueprint.outputs)[0]],true)
			}
			/*
			var check = (list,name)=>{
				if(!list){return}
				list.forEach((k,v)=>{
					if(!window.seen[k] && !ignored.includes(k)){
						console.log(name+": "+k,v,list)
						window.seen[k] = true
					}
				})
				
			}
			check(idata,"Generic")
			check(idata.weapon,"Weapon")
			check(idata.props,"Props")
			check(idata.slots,"Slots")
			check(idata.shipdef,"Station")
			check(idata.shipdef?.slots,"Station slots")
			q.idata.forEach((iname,idata)=>{
				check(idata,"Generic")
				check(idata.weapon,"Weapon")
				check(idata.props,"Props")
				check(idata.slots,"Slots")
				check(idata.shipdef,"Station")
				check(idata.shipdef?.slots,"Station slots")
			})*/
			var tt = func.tooltip2(parent,[box])
			tt.style.width = "320px"
			return tt
		},
		formatString(s){
			return s ? s.replaceAll("\n","<br>").replaceAll("\t","&nbsp;&nbsp;&nbsp;&nbsp;") : s
		},
		shipName(s,format){
			if(format==="character"){return s.custom_name ? s.custom_name+" #"+s.id : s.type+" #"+s.id}
			if(format==="test"){return s.custom_name ||"#"+s.id}
			if(format==="station"){return s.custom_name || s.name}
			if(format==="stranger"){
				if(s.custom_name){
					return s.custom_name
				}
				if(!s.id){
					return s.name
				}
				if(s.landmark){
					return s.name
				}
				return s.owner+" #"+s.id
			}
		},
		img_box(parent,width,height,src){
			var box = html.addElement(parent,"div")
			var img = html.addElement(box,"img")
			var w2 = width
			var h2 = height
			if(typeof(width) === "number"){
				w2 = width*0.8+"rem"
				width = width+"rem"
			}
			if(typeof(height) === "number"){
				h2 = height*0.8+"rem"
				height = height+"rem"
			}
			box.style.width = width
			box.style.height = height
			box.style.minWidth = width
			box.style.minHeight = height
			box.classList.add("centered")
			img.src = src
			img.style.maxWidth = w2
			img.style.maxHeight = h2
			return box
		},
		editable(parent,title,input_tag,initial,txt_open,txt_close,on_save){
			var box = html.addElement(parent,"div")
			box.classList.add("vertical")
			var box_top = html.addElement(box,"div")
			box_top.classList.add("horizontal")
			var title_div = html.addElement(box_top,"div",title)
			title_div.style.marginTop = "0.25rem"
			var content_parent = input_tag === "textarea" ? box : box_top
			var content = html.addElement(content_parent,"div")
			content.style.marginTop = "0.25rem"
			var editable = html.addElement(content_parent,input_tag)
			editable.style.minHeight = "1rem"
			var btn = html.addElement(box_top,"button",txt_open)
			btn.style.marginLeft = "auto"
			editable.onchange = ()=>{
				var val = editable.value
				val = val.replaceAll("<","")
				val = val.replaceAll(">","")
				content.innerHTML = val
			}
			editable.onblur = async()=>{
				if(func.input.mousedown){
					btn.style.pointerEvents = "none"
					await f.input.wait_mouseup()
					btn.style.pointerEvents = null
					btn.click()
				}
				else{
					btn.click()
				}
			}
			editable.style.display = "none"
			editable.value = initial
			content.innerHTML = initial
			var is_open = false
			btn.onclick = ()=>{
				if(document.activeElement === editable){return}
				is_open = !is_open
				content.style.display = is_open ? "none" : "initial"
				editable.style.display = is_open ? "initial" : "none"
				btn.innerHTML = is_open ? txt_close : txt_open
				if(is_open){
					editable.focus()
				}
				else{
					on_save(content.innerHTML)
				}
			}
			return editable
		},
		only_numbers(e){
			var el = e.target
			if(el.value === ""){return}
			var val = Number(el.value)
			if(isNaN(val) || !Number.isInteger(val)){
				el.value = el.saved_value
			}
			else if(val===0){
				el.value = ""
			}
			else{
				el.saved_value = val
				el.value = val
			}
		},
		next_tick(tick_type){
			time_per_tick = {
				"short": 60*5, // 5 minutes
				"long": 60*60*3, // 3 hours
				"day": 60*60*24 // 24 hours
			}
			var now = Date.now()/1000
			var then = Math.ceil(now/time_per_tick[tick_type])*time_per_tick[tick_type]
			return then-now
		},
		itype(item){
			if(q.idata[item]){
				if(q.idata[item].type){
					return q.idata[item]["type"]
				}
				return "other"
			}
			console.log("Unknown kind of item: "+item)
		},
		str_to_int(str){
			var hash = 0
			for (let i = 0; i < str.length; i++) {
				var char = str.charCodeAt(i) // Get ASCII code of character
				hash = (hash * 31 + char) | 0  // Multiply by a prime number and add char code
			}
			return hash >>> 0 // Ensure the hash is unsigned (32-bit positive integer)
		},
		error(txt){
			if(txt === func.prev_error){
				func.prev_err_count++
				html.forClass("error_display",e=>{
					e.innerHTML = txt+"("+func.prev_err_count+")"
				})
			}
			else{
				html.forClass("error_display",e=>{
					e.innerHTML = txt
				})
				func.prev_err_count = 1
			}
			func.prev_error = txt
			console.log(txt)
		},
		keydown(key,code){
			if(!func.keydown_handlers[key]){
				func.keydown_handlers[key] = []
			}
			func.keydown_handlers[key].push(code)
		},
		keydown_handler(e){
			if(e.altKey || e.ctrlKey || e.shiftKey){return}
			if(["INPUT","TEXTAREA"].includes(e.target.tagName)){return}
			var handlers = func.keydown_handlers[e.code] || []
			handlers.forEach(h=>h(e))
		},
		join_inv(amounts,idata){
			var result = {}
			Object.entries(amounts).forEach(e=>{
				var key = e[0]
				var amount = e[1]
				var entry = Object.assign({},idata[key])
				entry.amount = amount
				result[key] = entry
			})
			return result
		},
		async loaded(){
			var length = func.scripts.length
			await Promise.allSettled(func.scripts.map(s=>s.loaded))
			if(length !== func.scripts.length){
				await func.loaded()
			}
		},
		load(obj,path,key){
			switch(key){
				case "folders":
					Object.keys(obj).forEach(k=>{
						func.load(obj[k],path+k+"\\",k)
					})
					break
				case "files":
					obj.forEach(f=>{
						var script = document.createElement("script")
						script.src = path+f+".js"
						script.async = false
						var resolve,reject
						script.loaded = new Promise((yes,no)=>{
							resolve = yes
							reject = no
						})
						script.onload = ()=>{
							resolve()
						}
						script.onerror = ()=>{
							reject()
						}
						func.scripts.push(script)
						document.body.appendChild(script)
						//console.log("Filepath: "+path+f+".js")
					})
					break
				default:
					Object.keys(obj).forEach(k=>{
						func.load(obj[k],path,k)
					})
					break
			}
		}
	}
	var f = func
}
