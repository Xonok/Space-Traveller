func = {
	getSetting(name){
		return localStorage.getItem("settings:"+name)
	},
	setSetting(name,value){
		if(value === null || value === undefined){
			localStorage.removeItem("settings:"+name)
		}
		else{
			localStorage.setItem("settings:"+name,value)
		}
	},
	formatNumber(number){
		var locale = func.getSetting("locale") || undefined
		return number.toLocaleString(locale)
	},
	addElement(parent,type,inner){
		var e = document.createElement(type)
		if(inner!==undefined){e.innerHTML=inner}
		parent.append(e)
		return e
	},
	headers(parent,...names){
		var row = f.addElement(parent,"tr")
		row.type = "headers"
		names.forEach(n=>f.addElement(row,"th",n))
	},
	row(parent,...data){
		var r = f.addElement(parent,"tr")
		data.forEach(d=>{
			if(typeof d === "string" || typeof d === "number"){
				f.addElement(r,"td",d)
			}
			else if(d instanceof Element){
				f.addElement(r,"td").append(d)
			}
			else{
				console.log(d)
				throw new Error("Unknown element type for row.")
			}
		})
		return r
	},
	tooltip(parent,idata){
		var txt = idata.desc
		idata.prop_info?.forEach(i=>{
			txt += "<br>"+"&nbsp;".repeat(4)
			txt += i.value ? i.key+": "+i.value : i.key
		})
		var tt = f.addElement(parent,"span",func.formatString(txt))
		tt.className = "tooltiptext"
		return tt
	},
	formatString(s){
		return s.replaceAll("\n","<br>").replaceAll("\t","&nbsp;&nbsp;&nbsp;&nbsp;")
	},
	forClass(name,func){
		Array.from(document.getElementsByClassName(name)).forEach(func)
	},
	input(value,func){
		var e = document.createElement("input")
		if(value!=undefined && value != null){e.value = value}
		if(func){e.oninput = func}
		return e
	},
	only_numbers(e){
		var el = e.target
		if(el.value === ""){el.value = 0}
		var val = Number(el.value)
		if(isNaN(val) || !Number.isInteger(val)){
			el.value = el.saved_value || 0
		}
		else{
			el.saved_value = val
			el.value = val
		}
	}
}