f = func

function addSetting(id,name,def,verify){
	var box = f.addElement(window.settings_box,"div")
	var label = f.addElement(window.settings_box,"label",name)
	var input = f.addElement(window.settings_box,"input")
	var current = f.getSetting(id)
	if(!current){
		current = def
		f.setSetting(id,def)
	}
	input.value = current||""
	input.onchange = e=>{
		f.setSetting(id,e.target.value||null)
	}
}

addSetting("font","Font","Arial")
addSetting("locale","Locale")