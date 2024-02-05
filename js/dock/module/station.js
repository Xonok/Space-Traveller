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