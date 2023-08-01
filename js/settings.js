f = func

function addSetting(id,name,def,type,txt){
	var box = f.addElement(window.settings_box,"div")
	var label = f.addElement(window.settings_box,"label",name)
	var input = f.addElement(window.settings_box,"input")
	if(txt){
		f.addElement(window.settings_box,"label",txt)
	}
	if(type){
		input.type = type
	}
	var current = f.getSetting(id)
	if(!current){
		current = def
		f.setSetting(id,def)
	}
	input.value = current||""
	if(type==="checkbox"){
		input.checked = current
	}
	input.onchange = e=>{
		if(type==="checkbox"){
			f.setSetting(id,e.target.checked||null)
		}
		else{
			f.setSetting(id,e.target.value||null)
		}
		
	}
}

addSetting("font","Font","Arial")
addSetting("locale","Locale")
addSetting("rainbow_mode","Rainbow Mode","","checkbox","Very shiny reasonable stuffs.")
// how to add settings?
// rounded corners, added padding when you have a big screen?
// explain options? give examples?
// rainbow mode is either on or off, make it a checkbox?