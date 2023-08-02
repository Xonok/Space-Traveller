function change_name(){
	var name = window.custom_name.value
	send("update-name",{"structure":structure.name,"name":name})
}
function change_desc(){
	var desc = window.custom_desc.value
	send("update-desc",{"structure":structure.name,"desc":desc})
}

window.save_name.onclick = change_name
window.save_desc.onclick = change_desc
