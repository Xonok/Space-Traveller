var selected_option
function make_option(parent,id,name,desc,img_src){
	var div = f.addElement(parent,"div")
	div.classList.add("horizontal")
	var el = f.addElement(div,"input")
	el.setAttribute("type","radio")
	el.setAttribute("name","option")
	el.setAttribute("id",id)
	el.onchange = ()=>{
		selected_option = id
	}
	var img_box = f.img_box(div,"32px","32px",img_src)
	var label = f.addElement(div,"label",name+"<br>")
	label.setAttribute("for",id)
	var label_desc = f.addElement(label,"div",desc)
	label_desc.style.color = "pink"
	return el
}
function make_character(){
	selected_option = undefined
	var parent = window.new_character
	parent.innerHTML = ""
	parent.style.display = "initial"
	window.make_character_button.style.display = "none"
	var div = f.addElement(parent,"div")
	div.setAttribute("class","horizontal")
	f.addElement(div,"label","Character name: ")
	var input = f.addElement(div,"input")
	input.setAttribute("id","character_name")
	input.setAttribute("placeholder","Write your character's name here.")
	Object.entries(q.starters).forEach(e=>{
		var id = e[0]
		var data = e[1]
		var img = Object.entries(data.ships[0])[0][1].img
		make_option(parent,id,data.name,data.desc,img)
	})
	
	var btn_cancel = f.addElement(parent,"button","cancel")
	btn_cancel.onclick = ()=>{
		parent.style.display = "none"
		window.make_character_button.style.display = "initial"
	}
	var btn_make_character = f.addElement(parent,"button","make character")
	btn_make_character.onclick = ()=>{
		var character_name = document.getElementById('character_name').value;
		if(!character_name){
			window.error_display.innerHTML = "Name required."
			return
		}
		if(!selected_option){
			window.error_display.innerHTML = "Select a starting ship."
			return
		}
		f.send("make-character",{"new_cname":character_name,"starter":selected_option})
	}
}
function character_details(name,data){
	var parent = window.selected_character
	parent.innerHTML = ""
	parent.innerHTML += data.name+"<br>"
	parent.innerHTML += "Level: "+data.level+"<br>"
	parent.innerHTML += "Credits: "+func.formatNumber(data.credits)+"<br>"
	parent.innerHTML += "Room: "+data.stats.room.current+"/"+data.stats.room.max+"<br>"
	parent.innerHTML += "Location: "+data.active_ship.pos.system
	var flagship_box = f.addElement(parent,"div")
	flagship_box.classList.add("horizontal")
	flagship_box.innerHTML += "Flagship:"
	var img_box = f.img_box(flagship_box,"1.5rem","1.5rem",data.active_ship.img)
	img_box.style.marginLeft = "5px"
	img_box.style.marginRight = "5px"
	flagship_box.innerHTML += data.active_ship.custom_name || data.active_ship.name
	var fleet_box = f.addElement(parent,"div")
	fleet_box.classList.add("horizontal")
	fleet_box.innerHTML += "Fleet:&nbsp"
	Object.entries(data.ships).forEach((e,idx)=>{
		var [name,pship] = e
		if(name === data.active_ship.name){return}
		var img_box = f.img_box(fleet_box,"1.5rem","1.5rem",pship.img)
		if(idx){
			img_box.style.marginLeft = "-0.3rem"
		}
	})
	var date = new Date(data.last_active*1000).toLocaleString(func.getSetting("locale")||navigator.languages)
	parent.innerHTML += "Last played: "+date
	window.characters_selected_title.innerHTML = ""
	window.characters_selected_desc.innerHTML = ""
	f.editable(window.characters_selected_title,"Title:&nbsp","input",data.title||"","edit","save",title=>{
		f.send("update-character-title",{title})
	})
	f.editable(window.characters_selected_desc,"Description:&nbsp","textarea",data.desc||"","edit","save",desc=>{
		f.send("update-character-desc",{desc})
	})
	window.cancel_character.onclick = ()=>{
		window.box_selected_character.style.display = "none"
		window.box_make_character.style.display = "initial"
	}
	window.play_character.onclick = ()=>{
		f.view.open("nav")
	}
	window.box_make_character.style.display = "none"
	window.box_selected_character.style.display = "flex"
}
function selecting_character(){
	var character_list = window.character_list
	var active_char = sessionStorage.getItem("char") || q.active_character
	character_list.innerHTML = ""
	Object.entries(q.characters).forEach(e=>{
		var [name,data] = e
		var btn = f.addElement(character_list,"button")
		var img_box = f.img_box(btn,"22px","22px",data.active_ship.img)
		img_box.style.paddingRight = "5px"
		btn.className += " horizontal"
		btn.innerHTML += active_char === name ? "<b>"+name+"</b>" : name
		btn.onclick = ()=>{
			sessionStorage.setItem("char",name)
			delete q.pship
			delete q.cdata
			document.title = "Space Traveller: "+name
			character_details(name,data)
			selecting_character()
		}
	})
}

function characters_open(){
	window.box_selected_character.style.display = "none"
	window.box_make_character.style.display = "initial"
	window.make_character_button.onclick = make_character
	f.send("get-characters")
}
function characters_message(){
	selecting_character()
	window.new_character.style.display = "none"
	window.make_character_button.style.display = "initial"
}
f.view.register("characters",characters_open,characters_message)
