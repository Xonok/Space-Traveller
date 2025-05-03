function update_transport(){
	var tp = q.structure.transport
	if(!tp){return}
	window.lbl_transport_capacity.innerHTML = "Stored: "+tp.stored_power+"/"+tp.capacity
	window.lbl_transport_power.innerHTML = "Power: "+tp.power
	
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
		"owned": [["give","give to"],["take","take from"]],
		"any": [["buy","buy from"],["sell","sell to"]]
	}
	var headers = [{"delete":""},"action","target","item",{"amount":"#"},"limit","dist","cost","error"]
	var header_types = {
		"amount": "int+",
		"limit": "int+",
		"cost": "int+",
		"dist": "int+"
		
	}
	var t = f.make_table(window.tbl_transport,...headers)
	t.set_header_types(header_types)
	t.add_button("delete","delete",null,r=>{
		delete data[r.name]
		t.update(data)
	})
	t.add_dropdown("target",options_target,null,"pick something")
	t.add_dropdown("action",null,ogroup_action,"pick something")
	t.add_input("item","string",r=>{})
	t.add_input("amount","int+",r=>{})
	t.add_input("limit","int+",r=>{})
	t.force_headers(true)
	t.update(data)
	
	window.btn_transport_addline.onclick = e=>{
		last_idx++
		data = t.get_data()
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
			"entries": Object.values(t.get_data()).map(e=>f.dict_removes(e,"delete","error"))
		}
		console.log(table)
		send("update-transport",table)
	}
}