/*
CODE STATUS - initial
Things work, but could be improved:
*send is written from scratch instead being a standard function.
*Not all information provided by the server is used well. For example, #starter-descriptions
*The code hasn't been moved into its own folder, the way nav and trade have.
*/

var f=func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}
window.make_character_button.onclick=make_character

var starters = {}
function send(command,table={}){
	table.key = key
	table.command = command
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url
				return
			}
			window.error_display.innerHTML = ""
			var msg = JSON.parse(e.target.response)
			console.log(msg)
			starters = msg.starters
			selecting_character(msg)
		}
		else if(e.target.status===400){
			window.error_display.innerHTML = e.target.response
			console.log(e.target.response)
		}
		else if(e.target.status===400){
			window.error_display.innerHTML = "Server error."
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}

var selected_option
function make_option(parent,id,name,desc){
	var div = f.addElement(parent,"div")
	div.setAttribute("class","horizontal")
	var el = f.addElement(div,"input")
	el.setAttribute("type","radio")
	el.setAttribute("name","option")
	el.setAttribute("id",id)
	el.onchange = ()=>{
		selected_option = id
	}
	var desc= f.addElement(div,"label",desc)
	desc.setAttribute("style","color:pink;")
	var label = f.addElement(div,"label",name+"</br>")
	label.setAttribute("for",id)
	label.appendChild(desc)
	//#starter-descriptions
	//Turning this on adds the description, but that's ugly.
	//Task: find a way to display description without making things ugly.
	return el
}
function make_character(){
	selected_option = undefined
	window.new_character.style.display="initial"
	window.make_character_button.style.display="none"
	var new_character=window.new_character
	new_character.innerHTML=""
	var div0=f.addElement(new_character,"div")
	var div=f.addElement(div0,"div")
	div.setAttribute("class","horizontal")
	f.addElement(div,"label","Character name: ")
	var input=f.addElement(div,"input")
	input.setAttribute("id","character_name")
	var div2= f.addElement(div0,"div")
	div2.setAttribute("class","vertical")
	Object.entries(starters).forEach(e=>{
		var id = e[0]
		var data = e[1]
		make_option(div0,id,data.name,data.desc)
	})
	
	var button1=f.addElement(div0,"button","cancel")
	button1.onclick = ()=>{
		window.new_character.style.display="none"
		window.make_character_button.style.display="initial"
	}
	var button2=f.addElement(div0,"button","make character")
	button2.onclick = ()=>{
		var character_name = document.getElementById('character_name').value;
		if(!character_name){
			window.error_display.innerHTML = "Name required."
			return
		}
		if(!selected_option){
			window.error_display.innerHTML = "Select a starting ship."
			return
		}
		window.new_character.style.display="none"
		window.make_character_button.style.display="initial"
		console.log(character_name,selected_option)
		//return
		send("make-character",{"name":character_name,"starter":selected_option})
	}
}
function selecting_character(msg){
	var character_list=window.character_list
	character_list.innerHTML=""
	msg.characters.forEach(c=>{
		var label=f.addElement(character_list,"button",c)
		label.onclick = ()=>{
			send("select-character",{"character":c})
		}
	})
}

send("get-characters")

//Server will send a list of characters. Select one like this:
//send("select-character",{"character":"blah"})
//Make a new character like this:
//send("make-character",{"name":"Blorg","starter":"combat_stinger"})