// items
var f = func

function update_items_tables(){
	f.headers(window.items_ship,"","name","#","size","")
	f.headers(window.items_station2,"","name","#","size","change","")
	for(let [item,amount] of Object.entries(items)){
		make_item_row("ship",item,amount||0,idata[item].size_item || idata[item].size,amount_click_ship)
	}
	for(let [item,amount] of Object.entries(sinv.items)){
		let change = structure.market.change[item]||0
		if(change > 0){
			change = "+"+change
		}
		make_item_row2("station2",item,amount||0,idata[item].size_item || idata[item].size,change,amount_click_structure)
	}
	
	var bal = structure.market.balance
	var data = f.join_inv(items,idata)
	var data2 = f.join_inv(f.dict_merge({},sinv.items),idata)
	data2.forEach((k,v)=>{
		var change = structure.market.change[k]||0
		if(change > 0){
			change = "+"+change
		}
		v.change = change
	})
	var t = f.make_table(window.items_ship,{"img":""},"name",{"amount":"#"},"size",{"transfer":""})
	t.sort("name")
	t.add_class("name","dotted")
	t.add_class("amount","mouseover_underline")
	t.add_tooltip("name")
	t.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		var room_available = structure.inventory.room_left
		amount = Math.min(amount,Math.floor(room_available/idata[r.name].size))
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t.add_input("transfer","int+",null,0)
	t.force_headers(true)
	t.update(data)
	
	var t2 = f.make_table(window.items_station2,{"img":""},"name",{"amount":"#"},"size","change",{"transfer":""})
	t2.sort("name")
	t2.add_class("name","dotted")
	t2.add_class("amount","mouseover_underline")
	t2.add_tooltip("name")
	t2.add_onclick("amount",r=>{
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		var room_available = pship.inventory.room_left
		amount = Math.min(amount,Math.floor(room_available/idata[r.name].size))
		r.field["transfer"].value = r.field["transfer"].value ? "" : amount
	})
	t2.for_col("change",(div,r,name)=>{
		var item = name
		bal.produced[item] && bal.consumed[item] && div.classList.add("balance_neutral")
		bal.produced[item] && !bal.consumed[item] && div.classList.add("balance_positive")
		!bal.produced[item] && bal.consumed[item] && div.classList.add("balance_negative")
		//Hack to style each row based on what tech the item is
		var tech = idata[item].tech
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
					self: pship.name,
					other: structure.name,
					sgear: false,
					ogear: false,
					items: t.get_input_values("transfer")
				},
				{
					action: "take",
					self: pship.name,
					other: structure.name,
					sgear: false,
					ogear: false,
					items: t2.get_input_values("transfer")
				}
			]
		}
		send("transfer",table)
	}
}

window.transfer_credits_give.onclick = do_give_credits
function do_give_credits(){
	var give = Math.floor(Number(window.give_credits.value))
	give && send("give-credits",{"amount":give})
	window.give_credits.value = 0
}
window.transfer_credits_take.onclick = do_take_credits
function do_take_credits(){
	var take = Math.floor(Number(window.take_credits.value))
	take && send("take-credits",{"amount":take})
	window.take_credits.value = 0
}
window.store_all.onclick = do_storeall
function do_storeall(){
	var table = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: items
			}
		]
	}
	send("transfer",table)
}
window.take_all.onclick = do_takeall
function do_takeall(){
	var table = {
		data: [
			{
				action: "take",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: structure.inventory.items
			}
		]
	}
	send("transfer",table)
}
window.give_credits.onblur = f.only_numbers
window.take_credits.onblur = f.only_numbers
