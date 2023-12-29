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
	"shield": "Much protecc, regenerates, no repair bill."
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
	f.headers(window.sell_table,"","name","count","price","size","sell")
	var choice = commodity_categories.includes(active_tradetab) ? ["change"] : []
	f.headers(window.buy_table,"","name","count",...choice,"price","size","buy")
	for(let [item,data] of Object.entries(iprices)){
		if(itypes[active_tradetab].includes(item)){
			var size = idata[item].size_item || idata[item].size
			make_row("sell",item,items[item]||0,data.buy,size,amount_click_ship)
			let change = structure.market.change[item]||0
			if(change > 0){
				change = "+"+change
			}
			f.forClass("active_tradetab",c=>{if(!commodity_categories.includes(c.innerHTML)){change=undefined}})
			make_row2("buy",item,structure.inventory.items[item]||0,change,data.sell,size,amount_click_structure)
		}
	}
}
// trade sell
function make_row(name,item,amount,price,size,amount_func){
	//If price 0, don't add row.
	if(!price){return}
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	imgbox.classList.add("centered_")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.onmouseover=()=>{
		amount_div.style.textDecoration="underline"
	}
	amount_div.onmouseout=()=>{
		amount_div.style.textDecoration="none"
	}
	f.addElement(row,"td",f.formatNumber(price))
	f.addElement(row,"td",size)
	var input = make_input(row,name,item,transfer_info)
	amount_func(amount_div,amount,input)
	parent.appendChild(row)
}
// trade buy
function make_row2(name,item,amount,change,price,size,amount_func){
	//If price 0, don't add row.
	if(!price){return}
	var parent = window[name+"_table"]
	var row = document.createElement("tr")
	var imgbox = f.addElement(row,"td")
	imgbox.classList.add("centered_")
	f.addElement(imgbox,"img").src = idata[item].img
	var items = f.addElement(row,"td",idata[item].name)
	items.setAttribute("class","item_name "+name)
	f.tooltip(items,idata[item])
	var amount_div = f.addElement(row,"td",f.formatNumber(amount))
	amount_div.onmouseover=()=>{
		amount_div.style.textDecoration="underline"
	}
	amount_div.onmouseout=()=>{
		amount_div.style.textDecoration="none"
	}
	if(change!==undefined){
		var change_div = f.addElement(row,"td",change)
		var bal = structure.market.balance
		bal.produced[item] && bal.consumed[item] && change_div.classList.add("balance_neutral")
		bal.produced[item] && !bal.consumed[item] && change_div.classList.add("balance_positive")
		!bal.produced[item] && bal.consumed[item] && change_div.classList.add("balance_negative")
		change_div.onclick = ()=>{
			if(change < 0){
				var opposite_table_dict={"buy":"sell"}
				var opposite_table=opposite_table_dict[name]
				if(!opposite_table){throw new Error("Unknown table: " + name)}
				f.forClass(opposite_table,b=>{if(b.item===item){b.value=f.formatNumber(Number(b.value)+Math.abs(change))}})
			}
		}
		change_div.onmouseover=()=>{
			change_div.style.textDecoration="underline"
		}
		change_div.onmouseout=()=>{
			change_div.style.textDecoration="none"
		}
	}
	f.addElement(row,"td",f.formatNumber(price))
	f.addElement(row,"td",size)
	var input = make_input(row,name,item,transfer_info)
	amount_func(amount_div,amount,input)
	parent.appendChild(row)
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
				items: transfer.buy
			},
			{
				action: "sell",
				self: pship.name,
				other: structure.name,
				sgear: false,
				items: transfer.sell
			}
		]
	}
	if(!unpack){
		table.data[0].sgear = false
	}
	send("transfer",table)
}
window.sell_all.onclick = do_sellall
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
