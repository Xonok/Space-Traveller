function update_manage(){
	var parent = window.trade_setup
	f.headers(parent,"item","price(buy)","price(sell)","limit(buy)","limit(sell)")
	window.custom_name.value = structure.custom_name || ""
	window.custom_desc.value = structure.desc || ""
}
window.trade_setup.add_row = (e)=>{
	f.row(window.trade_setup,f.input(),f.input(0,f.only_numbers),f.input(0,f.only_numbers),f.input(0,f.only_numbers),f.input(0,f.only_numbers))
}


function change_name(){
	var name = window.custom_name.value
	send("update-name",{"structure":structure.name,"name":name})
}
function change_desc(){
	var desc = window.custom_desc.value
	send("update-desc",{"structure":structure.name,"desc":desc})
}

window.save_name.onclick = change_name
window.save_desc.onclick = change_desc

window.trade_setup_add_row.onclick = window.trade_setup.add_row
window.update_trade_prices.onclick = do_update_trade_prices
function do_update_trade_prices(){
	var table = {}
	window.trade_setup.childNodes.forEach(r=>{
		if(r.type === "headers"){return}
		var name = r.childNodes[0].childNodes[0].value
		var buy = Number(r.childNodes[1].childNodes[0].value)
		var sell = Number(r.childNodes[2].childNodes[0].value)
		var limit_buy = Number(r.childNodes[3].childNodes[0].value)
		var limit_sell = Number(r.childNodes[4].childNodes[0].value)
		if(!name){return}
		table[name] = {
			buy,
			sell,
			limit_buy,
			limit_sell
		}
	})
	if(!Object.keys(table).length){}
	send("update-trade",{"items":table})
}