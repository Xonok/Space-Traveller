function update_stats2(){
	var parent = window.station_stats
	var stats = structure.stats
	func.row(parent,"agility",stats.agility)
	func.row(parent,"armor",stats.armor.current+"/"+stats.armor.max)
	func.row(parent,"hull",stats.hull.current+"/"+stats.hull.max)
	func.row(parent,"shield",stats.shield.current+"/"+stats.shield.max)
	func.row(parent,"size",stats.size)
	func.row(parent,"speed",stats.speed)
	func.row(parent,"tracking",stats.tracking)
	func.row(parent,"weight",stats.weight)
	update_slots(window.station_slots,structure)
	
	var parent = window.ship_stats
	var stats = structure.stats
	var shipdef = ship_defs[structure.ship]
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
	var station_skill = cdata.skills.station_skill || 0
	if(shipdef.tech > station_skill){
		tt_text.tech += "<br><br>"+"Your station skill is too low for this station."
	}
	else{
		tt_text.tech += "<br><br>"+"Your station skill is good enough for this station."
	}
	var t = f.make_table(window.station_stats,{"name":"stat"},"value")
	t.add_class("value","centered")
	t.add_class("name","dotted")
	t.add_tooltip2("name",data=>{
		return tt_text[data.name] || "No description available."
	})
	t.update(data)
}

window.equip2.onclick = do_equip2
function do_equip2(){
	var table = {
		data: [
			{
				action: "give",
				self: structure.name,
				other: structure.name,
				sgear: false,
				ogear: true,
				items: make_list("item_station")
			},
			{
				action: "take",
				self: structure.name,
				other: structure.name,
				sgear: false,
				ogear: true,
				items: make_list("item_stationgear")
			}
		]
	}
	send("transfer",table)
}