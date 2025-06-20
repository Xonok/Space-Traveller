function group_open(){
	f.send("get-group-data")
}
function group_message(msg){
	group.display.update()
}
f.view.register("group",group_open,group_message)
