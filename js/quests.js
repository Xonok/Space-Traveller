function send(command,table={}){
	table.key = key
	table.command = command 
	var char = sessionStorage.getItem("char")
	if(char && !table.active_character){
		table.active_character = char
	}
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			window.error_display.innerHTML = ""
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url+window.location.search
				return
			}
			var msg = JSON.parse(e.target.response)
			console.log(msg)
		}
		else if(e.target.status===400){
			window.error_display.innerHTML = e.target.response
			console.log(e.target.response)
		}
		else if(e.target.status===500){
			window.error_display.innerHTML = "Server error."
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function update_quests(){
	
}


function quests_open(){
	f.send("get-quests")
}
function quests_message(msg){}
f.view.register("quests",quests_open,quests_message)
