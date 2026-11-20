function update_quests(){
	window.quest_lists.innerHTML=""
	q.character_quests.forEach((quest,info)=>{
		var parent = window.quest_lists
		var fieldset = html.addElement(parent,"fieldset")
		html.addElement(fieldset,"legend",info.title+"<br>")
		img_box = f.img_box(fieldset,"8rem","8rem",info.icon)
		html.addElement(fieldset,"div","Quest started in: "+info.start_location+"<br>")
		html.addElement(fieldset,"div","Given by: "+info.agent+"<br>")
		html.addElement(fieldset,"div","Short description of the quest: "+info.desc_short+"<br>")
		html.addElement(fieldset,"div","Long description of the quest: "+info.start_text+"<br>")
		info.objectives.forEach(o=>{
			var list = html.addElement(fieldset,"ul")
			var element = html.addElement(list,"li",o.desc)
			if(o.completed){
				element.style.textDecoration = "line-through"
			}
			if(o.status){
				element.innerHTML+=" ("+o.status + ")"
			}
		})
		console.log(q)
	})
}

function quests_open(){
	f.send("get-quests")
}
function quests_message(msg){
	update_quests()
}
f.view.register("quests",quests_open,quests_message)
