f = func

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
	if(type==="checkbox"){
		input.checked = current
	}
	if(txt){
		if(type==="checkbox"){
			// var txt2=input.checked? txt+": on":txt+": off"
		}
		var desc = f.addElement(window.settings_box,"label",txt)
		desc.classList.add("desc_label")
	}
	input.onchange = e=>{
		if(type==="checkbox"){
			f.setSetting(id,e.target.checked||null)
			// desc.innerHTML=e.target.checked? txt+": on":txt+ ": off"
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

addSetting("font","Font","Arial",null,null,(...args)=>console.log(...args))
addSetting("locale","Locale",null,null,"Affects number formating. Ex: &quot;et&quot; will format numbers like this: 9 123 456; &quot;en-gb&quot; will format numbers like this: 9,123,456") //https://www.andiamo.co.uk/resources/iso-language-codes/
addSetting("rainbow_mode","Rainbow Mode","","checkbox")
addSetting("serious_margin","Serious Margin",null,null,"If your screen is bigger and you want vibes, you can change the margin. Here's how this works: <a href=\"https://www.w3schools.com/Css/css_margin.asp\">CSS margin</a> ",null,"Ex: 50px 30px")
// rounded corners
// explain options? give examples?
// what are defaults for font, locale?
// link color scheme