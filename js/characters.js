var selected_option
function make_option(parent,id,name,desc,img_src){
	var div = f.addElement(parent,"div")
	div.setAttribute("class","horizontal")
	var el = f.addElement(div,"input")
	el.setAttribute("type","radio")
	el.setAttribute("name","option")
	el.setAttribute("id",id)
	el.onchange = ()=>{
		selected_option = id
	}
	var img_box = f.addElement(div,"div")
	img_box.style.width = "32px"
	img_box.style.height = "32px"
	var img = f.addElement(img_box,"img")
	img.src = img_src
	img.style.maxWidth = "32px"
	img.style.maxHeight = "32px"
	img.style.margin = "auto"
	img.style.display = "block"
	var desc= f.addElement(div,"label",desc)
	desc.setAttribute("style","color:pink;")
	var label = f.addElement(div,"label",name+"</br>")
	label.setAttribute("for",id)
	label.appendChild(desc)
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
	input.setAttribute("placeholder","Write your ship's name here.")
	var div2= f.addElement(div0,"div")
	div2.setAttribute("class","vertical")
	Object.entries(q.starters).forEach(e=>{
		var id = e[0]
		var data = e[1]
		var img = Object.entries(data.ships[0])[0][1].img
		make_option(div0,id,data.name,data.desc,img)
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
		f.send("make-character",{"cname":character_name,"starter":selected_option})
	}
}
function selecting_character(){
	var character_list = window.character_list
	var active_char = sessionStorage.getItem("char") || q.active_character
	character_list.innerHTML = ""
	Object.entries(q.characters).forEach(e=>{
		var [name,data] = e
		var btn = f.addElement(character_list,"button")
		var img_box = f.addElement(btn,"div")
		img_box.style.width = "22px"
		img_box.style.height = "22px"
		img_box.style.paddingRight = "5px"
		img_box.className="centered_"
		var img = f.addElement(img_box,"img")
		img.src = data.active_ship.img
		img.style.maxWidth = "20px"
		img.style.maxHeight = "20px"
		btn.className+=" horizontal"
		btn.innerHTML += active_char === name ? "<b>"+name+"</b>" : name
		btn.onclick = ()=>{
			sessionStorage.setItem("char",name)
			delete q.pship
			delete q.cdata
			f.view.open("nav")
			// f.send("select-character",{"character":name})
		}
	})
}

function characters_open(){
	window.make_character_button.onclick=make_character
	f.send("get-characters")
}
function characters_message(){
	selecting_character()
	window.new_character.style.display="none"
	window.make_character_button.style.display="initial"
}
f.view.register("characters",characters_open,characters_message)
