function update_stats2(){
	update_slots(window.station_slots,q.structure)
	
	var parent = window.ship_stats
	var stats = q.structure.stats
	var shipdef = q.ship_defs[q.structure.ship]
	var data = {
		"tech": shipdef.tech,
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
		"tech": "How difficult the station is to manage. If station skill is too low, stats are penalized and it's likely to miss ticks.",
		"tracking": "Improves the accuracy of weapons in combat. Having armor equipped does not penalize this.",
		"hull": "Hit points used for combat. Damage to hull points reduces speed and agility until repaired.",
		"armor": "Extra hit points that are lost before hull. Big hits can partly go through and as armor gets damaged that will happen more.<br><br>Durability: How much damage armor can take.",
		"soak": "How much damage the armor can take from a single hit. Any remaining damage hits hull.",
		"shield": "Extra hit points that are lost before hull and armor. A shield never lets damage pass through unless it runs out.",
		"shield_reg": "How much shield is regained after each round of combat."
	}
	var station_skill = q.cdata.skills.station || 0
	if(shipdef.tech > station_skill){
		tt_text.tech += "<br><br>"+"Your station skill is too low for this station."
	}
	else{
		tt_text.tech += "<br><br>"+"Your station skill is good enough for this station."
	}
	var t = f.make_table(window.station_stats,{"name":"stat"},"value")
	t.hide_headers(true)
	t.add_class("value","centered")
	t.add_tooltip2("name",data=>{
		return tt_text[data.name] || "No description available."
	})
	t.update(data)
}

function update_station_tables(){	
	var bal = q.structure.market.balance
	var data = f.join_inv(f.dict_merge({},q.structure.items),q.idata)
	var data2 = f.join_inv(f.dict_merge({},q.structure.gear),q.idata)
	data.forEach((k,v)=>{
		var change = q.structure.market.change[k]||0
		if(change > 0){
			change = "+"+change
		}
		v.change = change
	})
	
	var t = f.make_table(window.items_station,{"img":""},"name",{"amount":"#"},{"size":"size","alt":"size_item"},"change",{"transfer":""})
	t.sort("name")
	t.add_class("amount","mouseover_underline")
	t.add_item_tooltip("name")
	t.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		amount = Math.max(amount,0)	
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t.for_col("change",(div,r,name)=>{
		var item = name
		bal.produced[item] && bal.consumed[item] && div.classList.add("balance_neutral")
		bal.produced[item] && !bal.consumed[item] && div.classList.add("balance_positive")
		!bal.produced[item] && bal.consumed[item] && div.classList.add("balance_negative")
		//Hack to style each row based on what tech the item is
		var tech = q.idata[item].tech
		if(tech){
			div.parentNode.classList.add("style_tech_"+tech)
		}
	})
	t.add_class("change","mouseover_underline")
	t.add_onclick("change",r=>{
		var val = Number(r.field["change"].innerHTML)
		if(val > 0){
			r.field["transfer"].value = Number(r.field["transfer"].value) + val
		}
		else if(val < 0){
			var row = r.name
			var target_row = window.items_ship.table.rows[row]
			if(!target_row){return}
			var target_field = target_row.field["transfer"]
			target_field.value = Number(target_field.value) - val
		}
	})
	t.add_input("transfer","int+",null,0)
	t.force_headers(true)
	t.update(data)
	
	var t2 = f.make_table(window.items_stationgear,{"img":""},"name",{"amount":"#"},{"size":"size","alt":"size_item"},{"transfer":""})
	t2.sort("name")
	t2.add_class("amount","mouseover_underline")
	t2.add_item_tooltip("name")
	t2.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		amount = Math.max(amount,0)	
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t2.add_input("transfer","int+",null,0)
	t2.force_headers(true)
	t2.update(data2)
	
	window.equip2.onclick = ()=>{
		console.log(t.get_input_values("transfer"))
		console.log(t2.get_input_values("transfer"))
		var table = {
			data: [
				{
					action: "equip",
					self: q.structure.name,
					other: q.structure.name,
					items: t.get_input_values("transfer")
				},
				{
					action: "unequip",
					self: q.structure.name,
					other: q.structure.name,
					items: t2.get_input_values("transfer")
				}
			]
		}
		f.send("structure-trade",table)
	}
}
