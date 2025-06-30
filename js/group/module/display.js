group.display = {
	update(){
		window.input_group_create_name.value = ""
		window.input_group_transfer_name.value = ""
		window.input_group_apply_reason.value = ""
		window.box_group_create.style.display = !q.group ? "initial" : "none"
		window.box_group_mine.style.display = q.group ? "initial" : "none"
		window.btn_group_transfer.style.display = q.group?.leader === q.cdata.name ? "initial" : "none"
		window.btn_group_create.onclick = ()=>{
			var name = window.input_group_create_name.value
			f.send("group-create",{name})
		}
		window.btn_group_leave.onclick = ()=>{
			f.send("group-leave")
		}
		window.btn_group_transfer.onclick = ()=>{
			var new_leader = window.input_group_transfer_name.value
			f.send("group-transfer",{new_leader})
		}
		window.list_group_ranks.innerHTML = ""
		var ranks = []
		var add_rank = (name,start=true)=>{
			if(!name){return}
			if(ranks.includes(name)){return}
			var box = f.addElement(window.list_group_ranks,"div",null,start)
			box.classList.add("horizontal")
			var entry = f.addElement(box,"div",name)
			var btn = f.addElement(box,"button","Remove")
			if(start){
				ranks = [name,...ranks]
			}
			else{
				ranks.push(name)
			}
			btn.onclick = e=>{
				box.remove()
				ranks.remove(name)
			}
		}
		window.btn_rank_add.onclick = ()=>{
			add_rank(window.input_rank_name_new.value)
			window.input_rank_name_new.value = ""
		}
		window.btn_ranks_save.onclick = ()=>{
			f.send("group-modify-ranks",{ranks})
		}
		window.label_group_name.innerHTML = ""
		window.label_group_leader.innerHTML = ""
		window.list_group_members.innerHTML = ""
		window.list_group_applications.innerHTML = ""
		window.list_groups.innerHTML = ""
		window.box_list_groups.style.display = "initial"
		window.box_group_apply.style.display = "none"
		if(q.group){
			window.label_group_name.innerHTML = q.group.name
			window.label_group_leader.innerHTML = "Leader: "+q.group.leader
			q.group.members.forEach(name=>{
				var box = f.addElement(window.list_group_members,"div")
				box.classList.add("horizontal")
				var label_name = f.addElement(box,"div",name)
				if(q.group.leader === q.cdata.name){
					var select_rank = f.addElement(box,"select")
					q.group.ranks.forEach(r=>{
						var op = f.addElement(select_rank,"option",r)
						op.value = r
					})
					select_rank.value = q.group.member_rank[name]
					select_rank.onchange = ()=>{
						var rank = select_rank.value
						f.send("group-assign-rank",{name,rank})
					}
				}
				var btn_kick = f.addElement(box,"button","Kick")
				btn_kick.onclick = ()=>{
					f.send("group-kick",{name})
				}
			})
			q.group.applications.forEach((name,reason)=>{
				var box = f.addElement(window.list_group_applications,"div")
				box.classList.add("horizontal")
				var label_name = f.addElement(box,"div",name)
				f.tooltip2(label_name,reason)
				var btn_accept = f.addElement(box,"button","Accept")
				var btn_deny = f.addElement(box,"button","Deny")
				btn_accept.onclick = ()=>{
					f.send("group-accept",{name})
				}
				btn_deny.onclick = ()=>{
					f.send("group-deny",{name})
				}
			})
			q.group.ranks.forEach(r=>add_rank(r,false))
		}
		else{
			q.groups.forEach((k,v)=>{
				var group
				var box = f.addElement(window.list_groups,"div")
				box.classList.add("horizontal")
				var name = f.addElement(box,"div",v.name)
				var btn_apply = f.addElement(box,"button","Apply")
				btn_apply.onclick = ()=>{
					window.box_list_groups.style.display = "none"
					window.box_group_apply.style.display = "initial"
					window.label_group_apply_name.innerHTML = v.name
					window.input_group_apply_reason.value = ""
					group = k
				}
				window.btn_group_apply_cancel.onclick = ()=>{
					window.box_list_groups.style.display = "initial"
					window.box_group_apply.style.display = "none"
				}
				window.btn_group_apply_submit.onclick = ()=>{
					var reason = window.input_group_apply_reason.value
					f.send("group-apply",{group,reason})
				}
			})
		}
	}
}