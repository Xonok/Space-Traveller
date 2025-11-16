
if(JSON.parse(localStorage.getItem("dock_trade_unpack_ships"))){
	window.unpack_ships.checked = true
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
var itypes
function make_tradetab_buttons(){
	window.tradetabs.innerHTML = ""
	var buttons = []
	itypes = {}
	Object.keys(q.prices).forEach(item=>{
		var itype = q.idata[item].bp_category || f.itype(item)
		if(!itypes[itype]){
			itypes[itype] = []
		}
		itypes[itype].push(item)
	})
	if(!itypes[active_tradetab]){
		active_tradetab = null
	}
	Object.entries(tradetab_itypes).forEach(it2=>{
		var it = it2[0]
		var category = it2[1]
		if(!itypes[it]){return}
		var btn = f.addElement(window.tradetabs,"button",it)
		if(it===active_tradetab){btn.classList.add("category_active")}
		btn.classList.add("tradetab_category_"+category)
		btn.onclick = ()=>{
			//css styling needs class for styling the active button differently
			buttons.forEach(e=>e.classList.remove("category_active"))
			// f.forClass("category_active",e=>e.classList.remove("category_active"))
			active_tradetab = it
			btn.classList.add("category_active")
			window.sell_table.innerHTML=""
			window.buy_table.innerHTML=""
			update_trade_tables()
			// update_labels()
			window.custom_message.innerHTML = tradetab_message[active_tradetab] || ""
			window.ship_options.style.display = active_tradetab==="ship" ? "initial" : "none"
		}
		buttons.push(btn)
		!active_tradetab && btn.click()
	})
}
var commodity_categories = ["common","produced","rare"]
function update_trade_tables(){
	var tab_items = Object.keys(q.prices).filter(i=>{
		if(itypes[active_tradetab]?.includes(i)){
			return true
		}
		if(q.idata[i].slot === active_tradetab){
			return true
		}
		if(active_tradetab === q.idata[i].bp_category){
			return true
		}
	})
	var total_items = q.cdata.items
	var data = {}
	tab_items.forEach(i=>{
		data[i] = Object.assign({},q.idata[i])
		data[i].price = q.prices[i].buy
		data[i].limit = q.prices[i].limit_buy
		data[i].amount = total_items[i] || 0
	})
	var bal = q.structure.market.balance
	var headers = [{"img":""},"name",{"amount":"#"},"price","limit",{"size":"size","alt":"size_item"},"sell"]
	if(!commodity_categories.includes(active_tradetab)){
		headers = [{"img":""},"name",{"amount":"#"},"price","limit",{"size":"size","alt":"size_item"},"tech","sell"]
	}
	var t = f.make_table(window.sell_table,...headers)
	t.sticky_headers(true)
	t.sort("name","size","tech")
	t.show_grade("img")
	t.add_item_tooltip("name")
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

		var target_room = q.structure.stats.room.current
		var room_available = target_room - sell_room + buy_room
		
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		
		amount = Math.min(amount,Math.floor(room_available/q.idata[r.name].size))
		amount = Math.max(amount,0)	
		r.field["sell"].value = r.field["sell"].value ? "" : amount
	})
	t.format("price",e=>f.formatNumber(e.price))
	t.add_input("sell","number",f.only_numbers,0)
	t.for_col("name",(div,r,name)=>{
		var item = name
		//Hack to style each row based on what tech the item is
		var tech = q.idata[item].tech
		if(tech !== undefined){
			div.parentNode.classList.add("style_tech_"+tech)
		}
	})
	t.update(data)
	
	tab_items.forEach(i=>{
		data[i] = Object.assign({},q.idata[i])
		data[i].price = q.prices[i].sell
		data[i].limit = q.prices[i].limit_sell
		data[i].amount = q.structure.items[i] || 0
		data[i].change = q.structure.market.change[i] || 0
		if(data[i].change > 0){
			data[i].change = "+"+data[i].change
		}
	})
	var headers2 = [{"img":""},"name",{"amount":"#"},"change","price","limit",{"size":"size","alt":"size_item"},"buy"]
	if(!commodity_categories.includes(active_tradetab)){
		headers2 = [{"img":""},"name",{"amount":"#"},"price","limit",{"size":"size","alt":"size_item"},"tech","buy"]
	}
	var t2 = f.make_table(window.buy_table,...headers2)
	t2.sticky_headers(true)
	t2.sort("name","size","tech")
	t2.show_grade("img")
	t2.add_item_tooltip("name")
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

		var all_room = q.cdata.stats.room.current
		var room_available = all_room + sell_room - buy_room
		
		var amount = r.field["amount"].innerHTML.replace(/\D/g,"")
		
		amount = Math.min(amount,Math.floor(room_available/q.idata[r.name].size))
		amount = Math.max(amount,0)	
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
		var tech = q.idata[item].tech
		if(tech){
			div.parentNode.classList.add("style_tech_"+tech)
		}
	})
	t2.add_onclick("change",r=>{
		var val = Number(r.field["change"].innerHTML)
		if(val > 0){
			r.field["buy"].value = Number(r.field["buy"].value) + val
		}
		else if(val < 0){
			var row = r.name
			var target_field = window.sell_table.table.rows[row].field["sell"]
			target_field.value = Number(target_field.value) - val
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
				self: q.pship.name,
				other: q.structure.name,
				items: buy_table.table.get_input_values("buy")
			}*/
		]
	}
	var items_to_sell = sell_table.table.get_input_values("sell")
	var items_to_buy = buy_table.table.get_input_values("buy")
	if(Object.keys(items_to_sell).length){
		table.data.push({
			action: "sell",
			self: q.cdata.name,
			other: q.structure.name,
			items: items_to_sell
		})
	}
	if(Object.keys(items_to_buy).length){
		table.data.push({
			action: unpack ? "buy-ship" : "buy",
			self: q.cdata.name,
			other: q.structure.name,
			items: items_to_buy
		})
	}
	f.send("structure-trade",table)
}
window.sell_all.onclick = do_sellall
window.unpack_ships.onchange = e=>{
	localStorage.setItem("dock_trade_unpack_ships",JSON.stringify(e.target.checked))
}
function do_sellall(){
	var table = {
		data: []
	}
	
	var items_to_sell = Object.fromEntries(Object.entries(sell_table.table.get_values("amount",Number)).filter(d=>d[1]))
	table.data.push({
		action: "sell",
		self: q.cdata.name,
		other: q.structure.name,
		items: items_to_sell
	})
	f.send("structure-trade",table)
}
