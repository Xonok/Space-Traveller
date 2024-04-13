var tradetab_message = {
	"common": "Raw materials.",
	"produced": "Complex stuff made with machines.",
	"rare": "Exotic materials, not traded everywhere.",
	"gun": "Shoot rocks to make money. Shoot baddies to make die.",
	"factory": "Make stuff into other stuff. Stonks. If mini, can use in inventory. Otherwise need to equip and wait up to 3 hours.",
	"ship": "No refunds, but you can buy and use as many as you want.",
	"station_kit": "Put station on map. Now you have your own smol planet.",
	"expander": "Make station go big.",
	"armor": "Much protecc, very smol, must repair for big money.",
	"shield": "Much protecc, regenerates, no repair bill.",
	"drone": "Little helpers",
	"farm": "Produce stuff out of thin air!... or thin space, as the case may be."
}
var active_tradetab
function make_tradetab_buttons(){
	window.tradetabs.innerHTML = ""
	Object.keys(itypes).forEach((it,ID)=>{
		var btn = f.addElement(window.tradetabs,"button",it)
		if(it===active_tradetab){btn.className=" active_tradetab"}
		btn.onclick = ()=>{
			//css styling needs class for styling the active button differently
			f.forClass("active_tradetab",el=>{
				el.className = el.className.replace(" active_tradetab", "")
			})
			active_tradetab = it
			btn.className += " active_tradetab"
			transfer.reset()
			window.sell_table.innerHTML=""
			window.buy_table.innerHTML=""
			update_trade_tables()
			// update_labels()
			window.custom_message.innerHTML = tradetab_message[active_tradetab] || ""
			window.ship_options.style.display=active_tradetab==="ship"? "initial":"none"
		}
		!active_tradetab && !ID && btn.click()
	})
}
var commodity_categories = ["common","produced","rare"]
function update_trade_tables(){
	var tab_items = Object.keys(iprices).filter(i=>{
		if(itypes[active_tradetab].includes(i)){
			return true
		}
		if(active_tradetab === idata[i].bp_category){
			return true
		}
	})
	var total_items = {}
	if(window.sell_from_all.checked){
		Object.values(pships).forEach(ps=>{
			Object.entries(ps.inventory.items).forEach(e=>{
				var item = e[0]
				var amount = e[1]
				if(!total_items[item]){
					total_items[item] = 0
				}
				total_items[item] += amount
			})
		})
	}
	else{
		total_items = items
	}
	var data = {}
	tab_items.forEach(i=>{
		data[i] = Object.assign({},idata[i])
		data[i].price = iprices[i].buy
		data[i].amount = total_items[i] || 0
	})
	var bal = structure.market.balance
	var headers = [{"img":""},"name",{"amount":"#"},"price","size","sell"]
	if(!commodity_categories.includes(active_tradetab)){
		headers = [{"img":""},"name",{"amount":"#"},"price","size","tech","sell"]
	}
	var t = f.make_table(window.sell_table,...headers)
	t.sort("name","tech")
	t.add_tooltip("name")
	t.add_class("name","dotted")
	t.add_class("amount","mouseover_underline")
	t.format("amount",e=>f.formatNumber(e.amount))
	t.add_onclick("amount",r=>r.field["sell"].value = r.field["sell"].value ? "" : r.field["amount"].innerHTML)
	t.format("price",e=>f.formatNumber(e.price))
	t.add_input("sell","number",f.only_numbers,0)
	t.for_col("name",(div,r,name)=>{
		var item = name
		//Hack to style each row based on what tech the item is
		var tech = idata[item].tech
		if(tech !== undefined){
			div.parentNode.classList.add("style_tech_"+tech)
		}
	})
	t.update(data)
	
	tab_items.forEach(i=>{
		data[i] = Object.assign({},idata[i])
		data[i].price = iprices[i].sell
		data[i].amount = structure.inventory.items[i] || 0
		data[i].change = structure.market.change[i] || 0
		if(data[i].change > 0){
			data[i].change = "+"+data[i].change
		}
	})
	var headers2 = [{"img":""},"name",{"amount":"#"},"change","price","size","buy"]
	if(!commodity_categories.includes(active_tradetab)){
		headers2 = [{"img":""},"name",{"amount":"#"},"price","size","tech","buy"]
	}
	var t2 = f.make_table(window.buy_table,...headers2)
	t2.sort("name","tech")
	t2.add_tooltip("name")
	t2.add_class("name","dotted")
	t2.add_class("amount","mouseover_underline")
	t2.format("amount",e=>f.formatNumber(e.amount))
	t2.add_onclick("amount",r=>r.field["buy"].value = r.field["buy"].value ? "" : r.field["amount"].innerHTML)
	t2.format("price",e=>f.formatNumber(e.price))
	t2.add_class("change","mouseover_underline")
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
	t2.add_onclick("change",r=>{
		var val = Number(r.field["change"].innerHTML)
		if(val > 0){
			r.field["buy"].value = r.field["buy"].value ? "" : val
		}
		else if(val < 0){
			var row = r.name
			var target_field = window.sell_table.table.rows[row].field["sell"]
			target_field.value = target_field.value ? "" : -val
		}
	})
	t2.add_input("buy","number",f.only_numbers,0)
	t2.update(data)
}

window.transfer_button.onclick = do_transfer
function do_transfer(){
	var unpack = window.unpack_ships.checked && active_tradetab == "ship"
	var table = {
		data: [
			{
				action: unpack ? "buy-ship" : "buy",
				self: pship.name,
				other: structure.name,
				items: buy_table.table.get_input_values("buy")
			}
		]
	}
	var items_to_sell = sell_table.table.get_input_values("sell")
	if(window.sell_from_all.checked){
		Object.values(pships).forEach(ps=>{
			var items_from_ship = {}
			var sitems = ps.inventory.items
			Object.entries(items_to_sell).forEach(e=>{
				var item = e[0]
				var amount = e[1]
				if(sitems[item]){
					items_from_ship[item] = Math.min(sitems[item],amount)
					items_to_sell[item] -= items_from_ship[item]
					if(!items_to_sell[item]){
						delete items_to_sell[item]
					}
				}
			})
			if(Object.keys(items_from_ship).length){
				table.data.push({
					action: "sell",
					self: ps.name,
					other: structure.name,
					sgear: false,
					items: items_from_ship
				})
			}
		})
	}
	else{
		table.data.push({
			action: "sell",
			self: pship.name,
			other: structure.name,
			sgear: false,
			items: items_to_sell
		})
	}
	
	if(!unpack){
		table.data[0].sgear = false
	}
	send("transfer",table)
}
window.sell_all.onclick = do_sellall
window.sell_from_all.onchange = update_trade_tables
function do_sellall(){
	var sell = {}
	for(let [item,amount] of Object.entries(items)){
		if(itypes[active_tradetab].includes(item)){
			sell[item] = amount
		}
	}
	var table = {
		data: [
			{
				action: "sell",
				self: pship.name,
				other: structure.name,
				sgear: false,
				items: sell
			}
		]
	}
	send("transfer",table)
}
