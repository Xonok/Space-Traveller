// forEach could be better?
function update_stats(){
	var parent = window.ship_stats
	var stats = pship.stats
	func.row(parent,"size",stats.size)
	func.row(parent,"speed",stats.speed)
	func.row(parent,"agility",stats.agility)
	func.row(parent,"hull",stats.hull.current+"/"+stats.hull.max)
	func.row(parent,"armor",stats.armor.current+"/"+stats.armor.max)
	func.row(parent,"shield",stats.shield.current+"/"+stats.shield.max)
	update_slots(window.ship_slots,pship)
	console.log(ship_defs)
}

window.equip.onclick = do_equip
function do_equip(){
	var table = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: pship.name,
				sgear: false,
				ogear: true,
				items: make_list("off")
			},
			{
				action: "take",
				self: pship.name,
				other: pship.name,
				sgear: false,
				ogear: true,
				items: make_list("on")
			}
		]
	}
	send("transfer",table)
}
