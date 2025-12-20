function update_items_tables(){
	if(!q.structure){return}
	var bal = q.structure.market.balance
	var data = f.join_inv(q.cdata.items,q.idata)
	var data2 = f.join_inv(f.dict_merge({},q.structure.items),q.idata)
	data2.forEach((k,v)=>{
		var change = q.structure.market.change[k]||0
		if(change > 0){
			change = "+"+change
		}
		v.change = change
	})
	q.structure.market.change.forEach((k,v)=>{
		if(v > 0){
			v = "+"+v
		}
		if(!data2[k]){
			data2[k] = structuredClone(q.idata[k])
			data2[k].amount = 0
			data2[k].change = v
		}
	})
	var t = f.make_table(window.items_ship,{"img":""},"name",{"amount":"#"},{"size":"size","alt":"size_item"},{"transfer":""})
	t.sort("name")
	t.show_grade("img")
	t.add_class("amount","mouseover_underline")
	t.add_item_tooltip("name")
	t.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		var room_available = q.structure.stats.room.current
		amount = Math.min(amount,Math.floor(room_available/q.idata[r.name].size))
		amount = Math.max(amount,0)
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t.add_input("transfer","int+",null,0)
	t.force_headers(true)
	t.update(data)
	
	var t2 = f.make_table(window.items_station2,{"img":""},"name",{"amount":"#"},{"size":"size","alt":"size_item"},"change",{"transfer":""})
	t2.sort("name")
	t2.show_grade("img")
	t2.add_class("amount","mouseover_underline")
	t2.add_item_tooltip("name")
	t2.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		var room_available = q.cdata.stats.room.current
		amount = Math.min(amount,Math.floor(room_available/q.idata[r.name].size))
		amount = Math.max(amount,0)
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t2.for_col("change",(div,r,name)=>{
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
	t2.add_class("change","mouseover_underline")
	t2.add_onclick("change",r=>{
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
	t2.add_input("transfer","int+",null,0)
	t2.force_headers(true)
	t2.update(data2)
	
	window.transfer_button2.onclick = ()=>{
		console.log(t.get_input_values("transfer"))
		var table = {
			data: [
				{
					action: "give",
					self: q.cdata.name,
					other: q.structure.name,
					items: t.get_input_values("transfer")
				},
				{
					action: "take",
					self: q.cdata.name,
					other: q.structure.name,
					items: t2.get_input_values("transfer")
				}
			]
		}
		f.send("structure-trade",table)
	}
}

window.transfer_credits_give.onclick = do_give_credits
function do_give_credits(){
	var give = Math.floor(Number(window.give_credits_station.value))
	give && f.send("structure-give-credits",{"amount":give})
	window.give_credits_station.value = null
}
window.transfer_credits_take.onclick = do_take_credits
function do_take_credits(){
	var take = Math.floor(Number(window.take_credits.value))
	take && f.send("structure-take-credits",{"amount":take})
	window.take_credits.value = null
}
window.store_all.onclick = do_storeall
function do_storeall(){
	var table = {
		data: [
			{
				action: "give",
				self: q.cdata.name,
				other: q.structure.name,
				items: q.cdata.items
			}
		]
	}
	f.send("structure-trade",table)
}
window.take_all.onclick = do_takeall
function do_takeall(){
	var table = {
		data: [
			{
				action: "take",
				self: q.cdata.name,
				other: q.structure.name,
				items: q.structure.items
			}
		]
	}
	f.send("structure-trade",table)
}
window.give_credits_station.onblur = f.only_numbers
window.take_credits.onblur = f.only_numbers
