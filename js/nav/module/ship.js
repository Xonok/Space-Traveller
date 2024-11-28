nav.ship = {
	update_vitals(){
		var tab = "&nbsp;&nbsp;&nbsp;&nbsp;"
		var {hull,armor,shield} = pship.stats
		var xp_percent = Math.round(cdata.xp/10)
		window.vitals.innerHTML = "Level: "+cdata.level+" ("+xp_percent+"%)"+tab
		window.vitals.innerHTML += "Hull: "+hull.current+"/"+hull.max+tab
		window.vitals.innerHTML += "Armor: "+armor.current+"/"+armor.max+tab
		window.vitals.innerHTML += "Shield: "+shield.current+"/"+shield.max
	}
}