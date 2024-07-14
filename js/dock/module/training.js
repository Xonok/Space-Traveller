function update_training(){
	if(!skill_loc){return}
	var data = {}
	Object.entries(skill_loc).forEach(e=>{
		var key = e[0]
		var val = e[1]
		data[key] = Object.assign({},val,skill_data[key])
		data[key].current = cdata.skills[key] || 0
		data[key].cost = data[key].current+1
		if(val.item_req){
			var item_req = ""
			Object.entries(val.item_req).forEach(e2=>{
				var item = e2[0]
				var amount = e2[1]
				item_req += idata[item].name+": "+amount+"<br>"
			})
			data[key].item_req = item_req
		}
	})
	window.skill_char_info.innerHTML = "<span style=\"color:chocolate;font-weight:bold;\">"+cdata.name+"</span><br><br>Skill points: <b>"+cdata.skillpoints+"</b><br>XP: <b>"+cdata["xp"]+"/1000</b>"
	var t = f.make_table(window.tbl_training,{"name":"skill"},"max","current","cost","item_req","train")
	t.add_tooltip("name")
	t.add_class("name","dotted")
	t.add_button("train","Train",null,e=>train_skill(e.name))
	t.update(data)
	console.log(data)
}
function train_skill(name){
	send("skill-train",{name})
}