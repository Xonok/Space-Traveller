function display_user(msg){
	
}

function user_open(){
	f.send("get-user")
}
function user_message(msg){}
f.view.register("user",user_open,user_message)
