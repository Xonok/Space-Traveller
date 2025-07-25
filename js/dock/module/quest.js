function end_quest(){
	window.selected_quest.style.display = "initial"
	window.quest_desc.innerHTML = f.formatString(q.quest_end_text)
	window.quest_objectives.innerHTML = ""
	window.quest_hints.innerHTML = ""
	window.quest_objectives_label.style.display = "none"
	window.quest_hints_label.style.display = "none"
	window.cancel_quest.style = "display: none;" 
	window.submit_quest.style = "display: none;" 
}

function dock_update_quests(){
	window.quest_selection.innerHTML = ""
	var first_button
	if(!quest_ended){
		window.selected_quest.style.display = "none"
	}
	if(!Object.keys(q.local_quests).length){
		window.quest_selection.style.display="none"
	}
	else{window.quest_selection.style.display="initial"}
	Object.values(q.local_quests).forEach((qid,id)=>{
		console.log(qid)
		var outcome = qid.outcome
		var qbutton = f.addElement(window.quest_selection,"button",qid.title+"<br>")
		qbutton.setAttribute("id","quest_button")
		var sneak_peek=f.addElement(qbutton,"label",qid.desc_short)
		sneak_peek.style="font-size:10px;"
		first_button= id?undefined:qbutton
		qbutton.onclick = e=>{
			f.forClass("active_questbutton",b=>{
				b.classList.remove("active_questbutton")
				b.classList.remove("questcolour2")
			})
			qbutton.classList.add("active_questbutton")
			qbutton.classList.add("questcolour2")
			if(q.cdata.quests_completed[qid.name]){
				end_quest()
				return
			}
			window.quest_icon.setAttribute("src",qid.icon)
			window.quest_title.innerHTML = qid.title
			window.quest_desc.innerHTML = f.formatString(qid.start_text)
			var hints = window.quest_hints_label
			hints.innerHTML = ""
			var hint_list = window.quest_hints
			hint_list.innerHTML = ""
			window.quest_objectives_label.style.display = "initial"
			var goals = window.quest_objectives
			goals.innerHTML = ""
			if(outcome.hints){
				hints.innerHTML += "Hints:"
				outcome.hints?.forEach(h=>{
					f.addElement(hint_list,"li",h)
				})
			}
			if(!q.cdata.quests[qid.name]){
				outcome.objectives_text.forEach(ot=>{
					f.addElement(goals,"li",ot)
				})
			}
			else{
				qid.objectives.forEach(ot=>{
					if(ot.completed){
						f.addElement(goals,"li","<del>"+ot.desc+"</del>")
					}
					else{f.addElement(goals,"li",ot.desc+": "+ot.status)}
				})
			}
			var rewards = window.quest_rewards
			rewards.innerHTML = ""
			Object.entries(outcome.rewards).forEach(r=>{
				var name = r[0]
				var data = r[1]
				if(name === "credits"){
					f.addElement(rewards,"li",data+" credits.")
				}
				else if(name === "items"){
					var items_text = ""
					Object.entries(data).forEach(e=>{
						var name = e[0]
						var amount = e[1]
						items_text += q.idata[name].name+": "+amount+"<br>"
					})
					f.addElement(rewards,"div",items_text)
				}
				else{
					throw Error("Unknown reward type: "+name)
				}	
			})
			window.selected_quest.style.display = "initial"
			window.accept_quest.style = q.cdata.quests[qid.name] ? "display: none;" : "display: initial;"
			window.cancel_quest.style = q.cdata.quests[qid.name] ? "display: initial;" : "display: none;" 
			window.submit_quest.style = q.cdata.quests[qid.name] ? "display: initial;" : "display: none;" 
			window.accept_quest.onclick = ()=>{
				f.send("quest-accept",{"quest_id":qid.name})
			}
			window.cancel_quest.onclick = ()=>{
				f.send("quest-cancel",{"quest_id":qid.name})
			}
			window.submit_quest.onclick = ()=>{
				f.send("quest-submit",{"quest_id":qid.name})
			}
		}
		if(!quest_ended){
			first_button?.click()
		}
	})
}