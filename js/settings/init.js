function addSetting(id,name,def,type,txt,code,placeholder){
	var box = f.addElement(window.settings_box,"div")
	var label = f.addElement(window.settings_box,"label",name)
	var input = f.addElement(window.settings_box,"input")
	if(type){
		input.type = type
	}
	var current = f.getSetting(id)
	if(!current){
		current = def
		f.setSetting(id,def)
	}
	input.value = current||""
	input.placeholder=placeholder||""
	if(current==="Arial"){input.value="";input.placeholder="Arial"}
	if(type==="checkbox"){
		input.checked = current
	}
	if(txt){
		var desc = f.addElement(window.settings_box,"label",txt)
		desc.classList.add("desc_label")
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

function settings_open(){
	window.settings_box.innerHTML = ""
	addSetting("font","Font","Arial",null,null,(...args)=>console.log(...args))
	addSetting("locale","Locale",null,null,"Affects number formating. Ex: &quot;et&quot; will format numbers like this: 9 123 456; &quot;en-gb&quot; will format numbers like this: 9,123,456") //https://www.andiamo.co.uk/resources/iso-language-codes/
	addSetting("rainbow_mode","Rainbow Mode","","checkbox")
	addSetting("serious_margin","Serious Margin",null,null,"If your screen is bigger and you want &#10024;vibes&#10024;, you can change the margin. Here's how this works: <a id=\"margin\" href=\"https://www.w3schools.com/Css/css_margin.asp\" target=\"_blank\">CSS margin</a>",null,"Ex: 50px 30px")
	addSetting("grayscale","Grayscale Mode","","checkbox")
	// To do:
	// - rounded corners
}
function settings_message(msg){}

f.view.register("settings",settings_open,settings_message)