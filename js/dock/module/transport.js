function update_transport(){
	var tp = structure.transport
	window.lbl_transport_capacity.innerHTML = "Stored: "+tp.stored_power+"/"+tp.capacity
	window.lbl_transport_power.innerHTML = "Power: "+tp.capacity
	
	var data = {}
	var last_idx = -1
	tp.entries.forEach((e,idx)=>{
		last_idx = idx
		data[last_idx] = Object.assign({},e)
	})
	var options_target = []
	Object.values(transport_targets).forEach(t=>{
		if(t.name_custom){
			options_target.push([t.name,t.name_custom+" ("+t.name+")"])
		}
		else{
			options_target.push(t.name)
		}
	})
	var ogroup_action = {
		"owned": ["give","take"],
		"any": ["buy","sell"]
	}
	var headers = [{"next":"next?"},"delete","target","action","item",{"amount":"#"},"limit","dist","cost","error"]
	var header_types = {
		"amount": "int+",
		"limit": "int+",
		"cost": "int+",
		"dist": "int+"
		
	}
	var t = f.make_table(window.tbl_transport,...headers)
	t.set_header_types(header_types)
	t.add_dropdown("target",options_target)
	t.add_dropdown("action",null,ogroup_action)
	t.add_input("item","string",r=>{})
	t.add_input("amount","int+",r=>{})
	t.force_headers(true)
	t.update(data)
	
	window.btn_transport_addline.onclick = e=>{
		last_idx++
		data[last_idx] = {
			"target": "",
			"action": "",
			"item": "",
			"amount": 0,
			"limit": 0,
			"dist": 0,
			"cost": 0
		}
		t.update(data)
	}
	window.btn_transport_save.onclick = e=>{
		//Take data from table
		//Send to server
		var table = {
			"next_action": 0,
			"entries": Object.values(t.get_data()).map(e=>f.dict_removes(e,"next","delete","error"))
		}
		console.log(table)
		send("update-transport",table)
	}
}