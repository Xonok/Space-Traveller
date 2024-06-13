function update_training(){
	var data = {}
	Object.entries(skill_loc).forEach(e=>{
		var key = e[0]
		var val = e[1]
		data[key] = Object.assign({},val,skill_data[key])
		data[key].current = cdata.skills[key] || 0
		data[key].cost = data[key].current+1
	})
	window.skill_char_info.innerHTML = cdata.name+"<br>Level: "+cdata.level+"<br>Skill points: "+cdata.skillpoints
	var t = f.make_table(window.tbl_training,{"name":"skill"},"max","current","cost","train")
	t.add_button("train","Train",null,e=>train_skill(e.name))
	t.update(data)
	console.log(data)
}
function train_skill(name){
	send("skill-train",{name})
}