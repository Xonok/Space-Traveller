f = func

function addSetting(id,name,def,type,txt,code){
	var box = f.addElement(window.settings_box,"div")
	var label = f.addElement(window.settings_box,"label",name)
	var input = f.addElement(window.settings_box,"input")
	if(txt){
		var desc = f.addElement(window.settings_box,"label",txt)
		desc.classList.add("desc_label")
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
		config.apply()
		serious_margin.apply()
		if(code){
			var params = {
				box,
				label,
				input
			}
			if(txt){
				params.desc = desc
			}
			code(params)
		}
	}
}

addSetting("font","Font","Arial",null,"Text will look like this.",(...args)=>console.log(...args))
addSetting("locale","Locale",null,null,"blah")
addSetting("rainbow_mode","Rainbow Mode","","checkbox","Very shiny reasonable stuffs.")
addSetting("serious_margin","Serious Margin",null,null,"Make big screen less big use more space.")
// how to add settings?
// rounded corners, added padding when you have a big screen?
// explain options? give examples?
// rainbow mode is either on or off, make it a checkbox?