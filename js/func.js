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
	}
}