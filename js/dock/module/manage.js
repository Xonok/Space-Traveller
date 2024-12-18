function update_manage(){
	var parent = window.trade_setup
	f.headers(parent,"item","price(buy)","price(sell)","limit(buy)","limit(sell)")
	window.custom_name.value = structure.custom_name || ""
	window.custom_desc.value = structure.desc || ""
	update_production_summary()
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
function update_production_summary(){
	//TODO: handle "Time until empty"
	//TODO: time column in production table - it should say how long this thing can still be produced. (min of each component)
	window.production_input.innerHTML = ""
	window.production_output.innerHTML = ""
	window.production_none.innerHTML = ""
	window.consumption_none.innerHTML = ""
	if(cdata.name !== structure.owner){return}
	var input = {}
	var output = {}
	var items = structure.items
	Object.entries(structure.gear).forEach(e=>{
		var item = e[0]
		var amount = e[1]
		var data = idata[item]
		if(data.input){
			f.dict_add(input,f.dict_mult2(data.input,amount))
		}
		if(data.output){
			f.dict_add(output,f.dict_mult2(data.output,amount))
		}
	})
	var input_idata = f.join_inv(input,Object.fromEntries(Object.keys(input).map(k=>[k,structuredClone(idata[k])])))
	var output_idata = f.join_inv(output,Object.fromEntries(Object.keys(output).map(k=>[k,structuredClone(idata[k])])))
	Object.entries(input_idata).forEach(e=>{
		var item = e[0]
		var data = e[1]
		var ticks = Math.floor((items[item]||0)/data.amount)
		var hours = (ticks*3) % 24
		var days = Math.floor(ticks*3/24)
		data.time = ""
		data.time += days ? days+"d" : ""
		data.time += hours ? hours+"h" : ""
		if(!data.time){
			data.time = "No supply"
		}
	})
	var input_room = Object.values(input_idata).reduce((a,b)=>a+b.amount*b.size,0)
	var output_room = Object.values(output_idata).reduce((a,b)=>a+b.amount*b.size,0)
	var io_diff = output_room-input_room
	var ticks = Math.floor(structure.stats.room.current/io_diff)
	
	var days = Math.abs(Math.floor((ticks*3)/24))
	var hours = Math.abs((ticks*3) % 24)
	var time_string = ""
	time_string += days ? days+"d" : ""
	time_string += hours ? hours+"h" : ""
	var t = f.make_table(window.production_input,"img","name","amount","time")
	t.update(f.join_inv(input,input_idata))
	var t2 = f.make_table(window.production_output,"img","name","amount")
	t2.update(f.join_inv(output,output_idata))
	
	console.log(io_diff)
	if(io_diff < 0){
		//window.production_time_left.innerHTML = "Time left until empty: "+time_string
	}
	else{
		window.production_time_left.innerHTML = "Time left until full: "+time_string
	}
	if(!Object.keys(output).length){
		window.production_none.innerHTML = "None"
	}
	if(!Object.keys(input).length){
		window.consumption_none.innerHTML = "None"
	}
	if(!io_diff){
		window.production_time_left.innerHTML = ""
	}
	console.log(input,output,input_idata)
}