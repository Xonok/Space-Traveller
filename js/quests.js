function update_quests(){
	window.quest_lists.innerHTML=""
	q.character_quests.forEach((quest,info)=>{
		var parent = window.quest_lists
		var fieldset = f.addElement(parent,"fieldset")
		f.addElement(fieldset,"legend",info.title+"</br>")
		var img = f.addElement(fieldset,"img")
		img.setAttribute("src",info.icon)
		f.addElement(fieldset,"div","Quest started in: "+info.start_location+"</br>")
		f.addElement(fieldset,"div","Given by: "+info.agent+"</br>")
		f.addElement(fieldset,"div","Short description of the quest: "+info.desc_short+"</br>")
		f.addElement(fieldset,"div","Long description of the quest: "+info.start_text+"</br>")
		info.objectives.forEach(o=>{
			var list = f.addElement(fieldset,"ul")
			var element = f.addElement(list,"li",o.desc)
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
