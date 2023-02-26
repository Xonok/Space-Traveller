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
	}
}