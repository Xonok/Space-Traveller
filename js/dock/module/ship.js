function update_stats(){
	update_slots(window.ship_slots,pship)
	
	var parent = window.ship_stats
	var stats = pship.stats
	var shipdef = ship_defs[pship.type]
	var data = {
		"tech": shipdef.tech,
		"size": stats.size,
		"weight": stats.weight,
		"speed": stats.speed+"/"+shipdef.speed,
		"agility": stats.agility+"/"+shipdef.agility,
		"tracking": stats.tracking+"/"+(shipdef.tracking||0),
		"hull": stats.hull.current+"/"+stats.hull.max,
		"armor": stats.armor.current+"/"+stats.armor.max,
		"soak": stats.armor.soak,
		"shield": stats.shield.current+"/"+stats.shield.max,
		"shield_reg": stats.shield.reg
	}
	Object.entries(data).forEach(d=>{
		var key = d[0]
		var val = d[1]
		data[key] = {
			"name": key,
			"value": val
		}
	})
	var tt_text = {
		"tech": "How difficult the ship is to pilot. If piloting skill is too low, stats get penalized.",
		"size": "How big the ship is physically. Bigger ships are slowed down less by armor, but benefit less from stealth.",
		"weight": "Derived from size of the ship and the weight of armor. Makes cloaks less effective and decreases agility.",
		"speed": "Reduces delay between clicking to move and actually moving. With a high enough speed, the delay is 0.",
		"agility": "Improves dodging and the accuracy of weapons in combat. Equipped armor reduces this.",
		"tracking": "Improves the accuracy of weapons in combat. Having armor equipped does not penalize this.",
		"hull": "Hit points used for combat. Damage to hull points reduces speed and agility until repaired.",
		"armor": "Extra hit points that are lost before hull. Big hits can partly go through and as armor gets damaged that will happen more.<br><br>Durability: How much damage armor can take.",
		"soak": "How much damage the armor can take from a single hit. Any remaining damage hits hull.",
		"shield": "Extra hit points that are lost before hull and armor. A shield never lets damage pass through unless it runs out.",
		"shield_reg": "How much shield is regained after each round of combat."
	}
	var piloting = cdata.skills.piloting || 0
	if(shipdef.tech > piloting){
		tt_text.tech += "<br><br>"+"Your piloting skill is too low for this ship."
	}
	else{
		tt_text.tech += "<br><br>"+"Your piloting skill is good enough for this ship."
	}
	var t = f.make_table(window.ship_stats,{"name":"stat"},"value")
	t.hide_headers(true)
	t.add_class("value","centered")
	t.add_tooltip2("name",data=>{
		return tt_text[data.name] || "No description available."
	})
	t.update(data)
}
function update_slots(el,pship){
	var def = ship_defs[pship.ship || pship.type]
	var slots = {}
	for(let [key,value] of Object.entries(def.slots)){
		slots[key] = {
			current: 0,
			max: value
		}
	}
	Object.entries(pship.inventory.gear).forEach(item=>{
		var name = item[0]
		var amount = item[1]
		var def = idata[name]
		var slot = def.slot || def.type
		slots[slot].current += amount
	})
	var data = {}
	Object.entries(slots).forEach(s=>{
		var key = s[0]
		var val = s[1]
		if(val.max === -1){
			val.max = "inf"
		}
		data[key] = {
			"name": key,
			"value": val.current+"/"+val.max
		}
	})
	var t = f.make_table(el,{"name":"slot"},"value")
	t.hide_headers(true)
	t.add_class("value","centered")
	t.update(data)
}

var last_other_ship
function update_ship_tables(){
	var items_ship = f.join_inv(items,idata)
	var items_equipped = f.join_inv(gear,idata)
	var t = func.make_table(window.items_off,{"img":""},"name",{"amount":"#"},"size",{"transfer":""})
	t.sort("name")
	t.add_tooltip("name")
	t.add_class("amount","mouseover_underline")
	t.add_input("transfer","number",r=>{})
	t.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t.force_headers(true)
	t.update(items_ship)
	var t2 = func.make_table(window.items_on,{"img":""},"name",{"amount":"#"},"size",{"transfer":""})
	t2.sort("name")
	t2.add_tooltip("name")
	t2.add_class("amount","mouseover_underline")
	t2.add_input("transfer","number",r=>{})
	t2.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t2.force_headers(true)
	t2.update(items_equipped)
	
	window.equip.onclick = ()=>{
		var table = {
			data: [
				{
					action: "give",
					self: pship.name,
					other: pship.name,
					sgear: false,
					ogear: true,
					items: t.get_input_values("transfer")
				},
				{
					action: "take",
					self: pship.name,
					other: pship.name,
					sgear: false,
					ogear: true,
					items: t2.get_input_values("transfer")
				}
			]
		}
		send("transfer",table)
	}
	
	
	//Trade tab
	//need to copy ship targeting logic from nav inventory
	var t3 = f.make_table(window.ship_trade_items,{"img":""},"name",{"amount":"#"},{"size":"size","alt":"size_item"},{"transfer":""})
	t3.sort("name")
	t3.add_tooltip("name")
	t3.add_class("amount","mouseover_underline")
	t3.add_input("transfer","number")
	t3.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		//TODO: consider room
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t3.force_headers(true)
	t3.update(items_ship)
	
	window.other_name.innerHTML = ""
	Object.keys(pships).filter(n=>n!==pship.name).forEach(n=>{
		var op = f.addElement(window.other_name,"option",f.shipName(pships[n],"character"))
		op.value = n
	})
	
	window.other_name.onchange = e=>{
		var other_ship = e.target.value
		var other_pship = pships[other_ship]
		last_other_ship = other_ship
		//Temporary hack to avoid touching HTML
		window.give_credits_label.style.display = "none"
		window.give_credits_amount.style.display = "none"
		window.give_credits_ship.style.display = "none"
		//
		if(!other_pship){
			window.other_pack_ship.onclick = null
			window.ship_trade_other.innerHTML = ""
			window.ship_trade_transfer.style.display = "none"
			window.other_room.style.display = "none"
			window.other_pack_ship.style.display = "none"
			other_room_left = 999999
			return
		}
		window.other_pack_ship.onclick = ()=>{
			send("ship-pack",{"target":other_ship})
		}
		window.other_room.style.display = "initial"
		window.other_room.innerHTML = "Room left: "+String(other_pship.inventory.room_left)+"/"+String(other_pship.inventory.room_max+other_pship.inventory.room_extra)
		other_room_left = other_pship.inventory.room_left
		t4 = f.make_table(window.ship_trade_other,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
		t4.sort("name")
		t4.add_tooltip("name")
		t4.add_class("amount","mouseover_underline")
		t4.max_chars("name",24)
		t4.add_input("transfer","number",null,0)
		t4.add_onclick("amount",r=>{
			var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
			var room = pship.inventory.room_left
			var max = Math.floor(room/idata[r.name].size)
			amount = Math.min(amount,max)
			r.field["transfer"].value = r.field["transfer"].value ? "" : amount
		})
		t4.update(f.join_inv(other_pship.inventory.items,idata))
		window.empty_other.style = Object.keys(other_pship.inventory.items||{}).length ? "display:none" : "display:initial"
		window.ship_trade_transfer.style = "display:initial"
		window.other_pack_ship.style.display = Object.keys(other_pship.inventory.items||{}).length ? "none" : "initial"
	}
	if(last_other_ship === pship.name){
		last_other_ship = null
	}
	window.other_name.value = last_other_ship || Object.keys(pships).filter(n=>n!==pship.name)[0]
	window.other_name.onchange({target:window.other_name})
	
	window.ship_trade_transfer.onclick = ()=>{
		var table = {
			data: [
				/*{
					action: unpack ? "buy-ship" : "buy",
					self: pship.name,
					other: structure.name,
					items: buy_table.table.get_input_values("buy")
				}*/
			]
		}
		var items_to_give = t3.get_input_values("transfer")
		var items_to_take = t4.get_input_values("transfer")
		if(Object.keys(items_to_give).length){
			table.data.push({
				action: "give",
				self: pship.name,
				other: last_other_ship,
				sgear: false,
				ogear: false,
				items: items_to_give
			})
		}
		if(Object.keys(items_to_take).length){
			table.data.push({
				action: "take",
				self: pship.name,
				other: last_other_ship,
				sgear: false,
				ogear: false,
				items: items_to_take
			})
		}
		send("transfer",table)
	}
}