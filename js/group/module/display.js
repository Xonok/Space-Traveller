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
		//TODO: apply, accept, deny
		window.label_group_name.innerHTML = ""
		window.label_group_leader.innerHTML = ""
		window.list_group_members.innerHTML = ""
		window.list_group_applications.innerHTML = ""
		window.list_groups.innerHTML = ""
		window.box_list_groups.style.display = "initial"
		window.box_group_apply.style.display = "none"
		if(q.group){
			window.label_group_name.innerHTML = q.group.name
			window.label_group_leader.innerHTML = q.group.leader
			q.group.members.forEach(name=>{
				var box = f.addElement(window.list_group_members,"div")
				box.classList.add("horizontal")
				var label_name = f.addElement(box,"div",name)
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
		}
		else{
			//TODO: switch to a different UI when applying to a group.
			//Switch back when cancel.
			//Buttons: apply, apply_send, apply_cancel
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

/*
"name": "str",
"type": "str",
"leader": "str",
"members": "list:str"

do_group_create(cdata,name="str"):
do_group_apply(cdata,group="str",reason="str"):
do_group_accept(cdata,name="str"):
do_group_deny(cdata,name="str"):
do_group_leave(cdata):
do_group_transfer(cdata,new_leader="str"):

api.register("group-create",do_group_create)
api.register("group-apply",do_group_apply)
api.register("group-accept",do_group_accept)
api.register("group-deny",do_group_deny)
api.register("group-leave",do_group_leave)
api.register("group-transfer",do_group_transfer)
*/