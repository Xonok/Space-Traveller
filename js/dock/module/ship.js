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

function update_ship_tables(){
	var items_ship = f.join_inv(items,idata)
	var items_equipped = f.join_inv(gear,idata)
	var t = func.make_table(window.items_off,{"img":""},"name",{"amount":"#"},"size",{"transfer":""})
	t.add_tooltip("name")
	t.add_class("amount","mouseover_underline")
	t.add_input("transfer","number",r=>{})
	t.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t.update(items_ship)
	var t2 = func.make_table(window.items_on,{"img":""},"name",{"amount":"#"},"size",{"transfer":""})
	t2.add_tooltip("name")
	t2.add_class("amount","mouseover_underline")
	t2.add_input("transfer","number",r=>{})
	t2.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
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
}
