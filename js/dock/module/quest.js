var active_quest
function end_quest(){
	window.quest_desc.innerHTML = f.formatString(msg.quest_end_text)
	window.quest_objectives.innerHTML = ""
	window.cancel_quest.style = "display: none;" 
	window.submit_quest.style = "display: none;" 
}

function update_quests(){
	window.quest_selection.innerHTML = ""
	Object.values(quest_list).forEach(q=>{
		console.log(q)
		var outcome = q.outcome
		var qbutton = f.addElement(window.quest_selection,"button",q.title+"<br>")
		var sneak_peek=f.addElement(qbutton,"label",q.desc_short)
		sneak_peek.style="font-size:10px;"
		qbutton.style="border:solid #ff8531 1px;padding:10px; background-color:#ffac59;width:200px;"
		qbutton.onclick = e=>{
			active_quest=qbutton
			if(cdata.quests_completed[q.name]){
				end_quest()
				return
			}
			window.quest_icon.setAttribute("src",q.icon)
			window.quest_title.innerHTML=q.title
			window.quest_desc.innerHTML=q.start_text
			var goals = window.quest_objectives
			goals.innerHTML = ""
			if(!cdata.quests[q.name]){
				q.outcome.objectives_text.forEach(ot=>{
					f.addElement(goals,"li",ot)
				})
			}
			else{
				q.objectives.forEach(ot=>{
					if(ot.completed){
						f.addElement(goals,"li","<del>"+ot.desc+"</del>")
					}
					else{f.addElement(goals,"li",ot.desc+": "+ot.status)}
				})
			}
			var rewards = window.quest_rewards
			rewards.innerHTML = ""
			Object.entries(q.outcome.rewards).forEach(r=>{
				var name = r[0]
				var data = r[1]
				if(name === "credits"){
					f.addElement(rewards,"li",data+" credits.")
				}
				else{
					f.addElement(rewards,data+" "+idata[name].name)
				}	
			})
			window.selected_quest.style = "display: initial; background-color:#ffac59;"
			window.accept_quest.style = cdata.quests[q.name] ? "display: none;" : "display: initial;"
			window.cancel_quest.style = cdata.quests[q.name] ? "display: initial;" : "display: none;" 
			window.submit_quest.style = cdata.quests[q.name] ? "display: initial;" : "display: none;" 
			window.accept_quest.onclick = ()=>{
				send("quest-accept",{"quest-id":q.name})
			}
			window.cancel_quest.onclick = ()=>{
				send("quest-cancel",{"quest-id":q.name})
			}
			window.submit_quest.onclick = ()=>{
				send("quest-submit",{"quest-id":q.name})
			}
		}
		active_quest?.click()
	})
}