
if(localStorage.getItem("dock_trade_all_ships")){
	window.trade_all_ships.checked = true
}

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
var tradetab_itypes = {
	"common": "commodity",
	"produced": "commodity",
	"rare": "commodity",
	"artifact": "commodity",
	"ship": "gear",
	"gun": "gear",
	"missile": "gear",
	"drone": "gear",
	"armor": "gear",
	"shield": "gear",
	"aura": "gear",
	"sensor": "gear",
	"mining": "economy",
	"factory": "economy",
	"station_kit": "economy",
	"blueprint": "economy",
	"expander": "economy",
	"farm": "economy",
	"module": "economy",
	"transport": "economy"
}
var active_tradetab
function make_tradetab_buttons(){
	window.tradetabs.innerHTML = ""
	Object.entries(tradetab_itypes).forEach((it2,ID)=>{
		var it = it2[0]
		var category = it2[1]
		if(!Object.keys(itypes).includes(it)){return}
	//Object.keys(itypes).forEach((it,ID)=>{
		var btn = f.addElement(window.tradetabs,"button",it)
		if(it===active_tradetab){btn.classList.add("active_tradetab")}
		btn.classList.add("tradetab_category_"+category)
		btn.onclick = ()=>{
			//css styling needs class for styling the active button differently
			f.forClass("active_tradetab",e=>e.classList.remove("active_tradetab"))
			active_tradetab = it
			btn.classList.add("active_tradetab")
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
		if(itypes[active_tradetab]?.includes(i)){
			return true
		}
		if(idata[i].slot === active_tradetab){
			return true
		}
		if(active_tradetab === idata[i].bp_category){
			return true
		}
	})
	var total_items = {}
	if(window.trade_all_ships.checked){
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
	var headers = [{"img":""},"name",{"amount":"#"},"price",{"size":"size","alt":"size_item"},"sell"]
	if(!commodity_categories.includes(active_tradetab)){
		headers = [{"img":""},"name",{"amount":"#"},"price",{"size":"size","alt":"size_item"},"tech","sell"]
	}
	var t = f.make_table(window.sell_table,...headers)
	t.sort("name","size","tech")
	t.add_tooltip("name")
	t.add_class("name","dotted")
	t.add_class("amount","mouseover_underline")
	t.format("amount",e=>f.formatNumber(e.amount))
	t.add_onclick("amount",r=>{
		var sell_amounts = t.get_values("sell",Number)
		var sell_sizes = t.get_values("size",Number)
		var sell_room_table = f.dict_mult(sell_amounts,sell_sizes)
		var sell_room = f.dict_sum(sell_room_table)
		
		var buy_amounts = t2.get_values("buy",Number)
		var buy_sizes = t2.get_values("size",Number)
		var buy_room_table = f.dict_mult(buy_amounts,buy_sizes)
		var buy_room = f.dict_sum(buy_room_table)

		var target_room = structure.inventory.room_left
		var room_available = target_room - sell_room + buy_room
		
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		
		amount = Math.min(amount,Math.floor(room_available/idata[r.name].size))
		r.field["sell"].value = r.field["sell"].value ? "" : amount
	})
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
	var headers2 = [{"img":""},"name",{"amount":"#"},"change","price",{"size":"size","alt":"size_item"},"buy"]
	if(!commodity_categories.includes(active_tradetab)){
		headers2 = [{"img":""},"name",{"amount":"#"},"price",{"size":"size","alt":"size_item"},"tech","buy"]
	}
	var t2 = f.make_table(window.buy_table,...headers2)
	t2.sort("name","size","tech")
	t2.add_tooltip("name")
	t2.add_class("name","dotted")
	t2.add_class("amount","mouseover_underline")
	t2.format("amount",e=>f.formatNumber(e.amount))
	t2.add_onclick("amount",r=>{
		var sell_amounts = t.get_values("sell",Number)
		var sell_sizes = t.get_values("size",Number)
		var sell_room_table = f.dict_mult(sell_amounts,sell_sizes)
		var sell_room = f.dict_sum(sell_room_table)
		
		var buy_amounts = t2.get_values("buy",Number)
		var buy_sizes = t2.get_values("size",Number)
		var buy_room_table = f.dict_mult(buy_amounts,buy_sizes)
		var buy_room = f.dict_sum(buy_room_table)

		var all_room = Object.values(pships).map(ps=>ps.inventory.room_left).reduce((a,b)=>a+b,0)
		var target_room = window.trade_all_ships.checked ? all_room : pship.inventory.room_left
		var room_available = target_room + sell_room - buy_room
		
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		
		amount = Math.min(amount,Math.floor(room_available/idata[r.name].size))
		r.field["buy"].value = r.field["buy"].value ? "" : amount
	})
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
			/*{
				action: unpack ? "buy-ship" : "buy",
				self: pship.name,
				other: structure.name,
				items: buy_table.table.get_input_values("buy")
			}*/
		]
	}
	var items_to_sell = sell_table.table.get_input_values("sell")
	var items_to_buy = buy_table.table.get_input_values("buy")
	if(window.trade_all_ships.checked){
		Object.values(pships).forEach(ps=>{
			var items_from_ship = {}
			var items_to_ship = {}
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
			var items_room = 0
			var items_sizes = Object.entries(items_from_ship).forEach(e=>{
				items_room += idata[e[0]].size*e[1]
			})
			var ship_room = ps.inventory.room_left + items_room
			Object.entries(items_to_buy).forEach(e=>{
				var item = e[0]
				var amount = e[1]
				var max = Math.floor(ship_room/idata[e[0]].size)
				items_to_ship[item] = Math.min(max,amount)
				items_to_buy[item] -= items_to_ship[item]
				if(!items_to_buy[item]){
					delete items_to_buy[item]
				}
			})
			if(Object.keys(items_to_ship).length){
				table.data.push({
					action: unpack ? "buy-ship" : "buy",
					self: ps.name,
					other: structure.name,
					items: items_to_ship
				})
				table.data.last().sgear = false
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
window.trade_all_ships.onchange = e=>{
	localStorage.setItem("dock_trade_all_ships",e.target.checked)
	update_trade_tables()
	update_labels()
}
function do_sellall(){
	var table = {
		data: []
	}
	
	var items_to_sell = Object.fromEntries(Object.entries(sell_table.table.get_values("amount",Number)).filter(d=>d[1]))
	if(window.trade_all_ships.checked){
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
	send("transfer",table)
}
