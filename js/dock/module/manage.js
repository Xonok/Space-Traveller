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
	var tile_name = ctx.tile.terrain
	var tile_res = {
		"energy": "energy",
		"nebula": "gas",
		"asteroids": "ore",
		"exotic": "exotic_matter",
		"phase": "phase_vapor"
	}
	var res_name = tile_res[tile_name]
	var res_idata = ctx.idata[res_name]
	Object.entries(structure.gear).forEach(e=>{
		var item = e[0]
		var amount = e[1]
		var data = idata[item]
		//Only items with station_mining give any mining-related stats or bonuses to stations
		if(data.props?.station_mining){
			var mining_power = data.props["mining_power_"+tile_name]
			var mining_amount = mining_power*100/res_idata.price
			var res_data = {
				[res_name]: mining_amount*amount
			}
			f.dict_add(output,res_data)
			if(data.props["mining_bonus_"+tile_name]){
				data.props["mining_bonus_"+tile_name].forEach((k,v)=>{
					var bonus_item = k
					var bonus_idata = ctx.idata[bonus_item]
					var bonus_amount = v*100/bonus_idata.price
					var res_data2 = {
						[bonus_item]: bonus_amount*amount
					}
					f.dict_add(output,res_data)
				})
			}
		}
		if(data.input){
			f.dict_add(input,f.dict_mult2(data.input,amount))
		}
		if(data.output){
			f.dict_add(output,f.dict_mult2(data.output,amount))
		}
	})
	var old_limits = structure.props?.limits || {}
	old_limits.forEach((k,v)=>{
		output[k] = output[k] || 0
	})
	output = output.map(Math.round)
	
	var input_idata = f.join_inv(input,Object.fromEntries(Object.keys(input).map(k=>[k,structuredClone(idata[k])])))
	var output_idata = f.join_inv(output,Object.fromEntries(Object.keys(output).map(k=>[k,structuredClone(idata[k])])))
	old_limits.forEach((k,v)=>{
		var data = output_idata[k] || {}
		data.limit = v
		output_idata[k] = data
	})
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
	var t2 = f.make_table(window.production_output,"img","name","amount","limit")
	t2.add_input("limit","int+",f.only_numbers)
	t2.update(f.join_inv(output,output_idata))
	
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
	window.btn_update_prod_limits.onclick = e=>{
		var limits = t2.get_input_values("limit")
		console.log(limits)
		send("structure-update-limits",{limits})
	}
}