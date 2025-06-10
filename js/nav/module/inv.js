var usable_items = []
function update_inventory(){
	window.ship_name.value = "Ship: " + f.shipName(q.pship,"character")
	var stats = q.cdata.stats
	var items = q.cdata.items
	var gear = q.pship.gear
	window.room.innerHTML = "Room left: "+func.formatNumber(stats.room.current)+"/"+func.formatNumber(stats.room.max)
	var chars_short = 17
	var chars_wide = 30
	
	//gear tab
	//I wish headers were easier to define. The object syntax is a mess and unneeded.
	//Arrays would be better
	usable_items = []
	var t = f.make_table(window.inv_gear_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"})
	t.sort("name")
	t.add_item_tooltip("name")
	t.add_class("name","full_btn")
	t.max_chars("name",chars_short)
	t.add_button("name",null,{"usable":true},r=>{
		console.log(r,r.name)
		f.send("use-item",{"item":r.name})
	})
	t.for_col("name",(div,r,name)=>{
		if(t.data[name].usable){
			usable_items.push(name)
			div.innerHTML += "("+String(usable_items.length)+")"
		}
	})
	t.update(f.join_inv(items,q.idata))
	
	var factories = q.pship.stats.factories
	var t2 = f.make_table(window.gear_list,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"})
	t2.sort("name")
	t2.add_item_tooltip("name")
	t2.add_class("name","full_btn")
	t2.max_chars("name",chars_wide)
	t2.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);f.send("use-item",{"item":r.name})})
	t2.for_col("name",(div,r,name)=>{
		if(t2.data[name].usable){
			if(!usable_items.includes(name)){usable_items.push(name)}
			div.innerHTML += "("+String(usable_items.indexOf(name)+1)+")"
			if(factories[name]){
				var charges = factories[name]["cur"]+"/"+factories[name]["max"]
				div.innerHTML += "("+charges+")"
			}
		}
	})
	t2.update(f.join_inv(gear,q.idata))
	f.forClass("empty_inv",e=>{
		e.style = Object.keys(items).length ? "display:none" : "display:initial"
	})
	window.empty_gear.style = Object.keys(gear).length ? "display:none" : "display:initial"
	//loot tab
	var t3 = f.make_table(window.inv_loot_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t3.sort("name")
	t3.add_item_tooltip("name")
	t3.add_class("name","full_btn")
	t3.add_class("amount","mouseover_underline")
	t3.max_chars("name",chars_short)
	t3.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);f.send("use-item",{"item":r.name})})
	t3.add_input("transfer","number",null,0)
	t3.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t3.for_col("name",(div,r,name)=>{
		if(t3.data[name].usable){
			div.innerHTML += "("+String(usable_items.indexOf(name)+1)+")"
		}
	})
	t3.update(f.join_inv(items,q.idata))
	
	var t4 = f.make_table(window.inv_loot_loot,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t4.sort("name")
	t4.add_item_tooltip("name")
	t4.add_class("amount","mouseover_underline")
	t4.max_chars("name",chars_short)
	t4.add_input("transfer","number",null,0)
	t4.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		var room = q.cdata.stats.room.current
		var max = Math.floor(room/q.idata[r.name].size)
		amount = Math.min(amount,max)
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t4.update(f.join_inv(q.tile.items||{},q.idata))
	window.empty_loot.style = Object.keys(q.tile.items||{}).length ? "display:none" : "display:initial"
	
	window.drop_all.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.drop.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.loot_all.style = Object.keys(q.tile.items||{}).length ? "display:initial" : "display:none"
	window.loot.style = Object.keys(q.tile.items||{}).length ? "display:initial" : "display:none"
	window.drop.onclick = ()=>do_drop(t3.get_input_values("transfer"))
	window.loot.onclick = ()=>do_loot(t4.get_input_values("transfer"))
	//trade tab
	var other_room_left
	var t5 = f.make_table(window.inv_trade_inventory,"img",{"name":"item"},{"amount":"#"},{"size":"size","alt":"size_item"},"transfer")
	t5.sort("name")
	t5.add_item_tooltip("name")
	t5.add_class("name","full_btn")
	t5.add_class("amount","mouseover_underline")
	t5.max_chars("name",chars_short)
	t5.add_button("name",null,{"usable":true},r=>{console.log(r,r.name);f.send("use-item",{"item":r.name})})
	t5.add_input("transfer","number",null,0)
	t5.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		var max = Math.floor(other_room_left/q.idata[r.name].size)
		amount = Math.min(amount,max)
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t5.for_col("name",(div,r,name)=>{
		if(t5.data[name].usable){
			div.innerHTML += "("+String(usable_items.indexOf(name)+1)+")"
		}
	})
	t5.update(f.join_inv(items,q.idata))
	
	var names = []
	window.other_name.innerHTML = ""
	Object.keys(q.tile.ships).forEach(owner=>{
		if(owner === q.cdata.name){return}
		if(q.map_characters[owner].npc){return}
		var op = f.addElement(window.other_name,"option",owner)
		op.value = owner
		names.push(owner)
	})
	if(!names.length){
		window.other_room.innerHTML = ""
	}
	window.give_credits_amount.value = ""
	window.other_name.onchange = e=>{
		var other_character = e.target.value
		other_cdata = q.map_characters[other_character]
		window.give_credits.onclick = ()=>{
			var target = other_character
			var amount = Math.floor(Number(window.give_credits_amount.value))
			f.send("give-credits-character",{target,amount})
		}
		window.other_room.innerHTML = "Room left: "+String(other_cdata.stats.room.current)+"/"+String(other_cdata.stats.room.max)
		other_room_left = other_cdata.stats.room.current
	}
	window.other_name.value && window.other_name.onchange({target:{value:window.other_name.value}})
	window.give.style = Object.keys(items).length ? "display:initial" : "display:none"
	window.give.onclick = ()=>{
		var table = {
			data: [
				{
					action: "give",
					self: q.cdata.name,
					other: window.other_name.value,
					items: t5.get_input_values("transfer")
				}
			]
		}
		f.send("ship-trade",table)
	}
}