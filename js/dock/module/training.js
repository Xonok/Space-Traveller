function update_training(){
	if(!q.skill_location){return}
	var data = {}
	Object.entries(q.skill_location).forEach(e=>{
		var key = e[0]
		var val = e[1]
		data[key] = Object.assign({},val,q.skill_data[key])
		data[key].current = q.cdata.skills[key] || 0
		data[key].cost = data[key].current+1
		if(q.cdata.skills[key] >= data[key].max){
			data[key].cost = ""
		}
		if(val.item_req){
			var item_req = ""
			Object.entries(val.item_req).forEach(e2=>{
				var item = e2[0]
				var amount = e2[1]
				item_req += q.idata[item].name+": "+amount+"<br>"
			})
			data[key].item_req = item_req
		}
	})
	window.skill_char_info.innerHTML = "<span style=\"color:chocolate;font-weight:bold;\">"+q.cdata.name+"</span><br><br>Skill points: <b>"+q.cdata.skillpoints+"</b><br>XP: <b>"+q.cdata["xp"]+"/1000</b>"
	var t = f.make_table(window.tbl_training,{"name":"skill"},"max","current","cost","item_req","train")
	t.add_tooltip("name")
	t.add_button("train","Train",null,e=>train_skill(e.name))
	t.update(data)
}
function train_skill(name){
	f.send("skill-train",{name})
}