var f=func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}
window.make_character_button.onclick=make_character

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

function make_character(){
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
	var div3= f.addElement(div0,"div")
	div3.setAttribute("class","horizontal")
	var radio1=f.addElement(div3,"input")
	radio1.setAttribute("type","radio")
	radio1.setAttribute("name","option")
	radio1.setAttribute("id","combat")
	var label1=f.addElement(div3,"label","combat stinger")
	label1.setAttribute("for","combat")
	var div4= f.addElement(div0,"div")
	div4.setAttribute("class","horizontal")
	var radio2=f.addElement(div4,"input")
	radio2.setAttribute("type","radio")
	radio2.setAttribute("name","option")
	radio2.setAttribute("id","trade")
	var label2=f.addElement(div4,"label","trade beetle")
	label2.setAttribute("for","combat")
	
	var button1=f.addElement(div0,"button","cancel")
	button1.onclick = ()=>{
		window.new_character.style.display="none"
		window.make_character_button.style.display="initial"
	}
	var button2=f.addElement(div0,"button","make character")
	button2.onclick = ()=>{
		var character_name = document.getElementById('character_name').value;
		var trade = document.getElementById('trade').checked
		if(trade==true && character_name){
			window.new_character.style.display="none"
			window.make_character_button.style.display="initial"
			send("make-character",{"name":character_name,"starter":"trade_beetle"})
		}
		else if(character_name){
			window.new_character.style.display="none"
			window.make_character_button.style.display="initial"
			send("make-character",{"name":character_name,"starter":"combat_stinger"})
		}
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