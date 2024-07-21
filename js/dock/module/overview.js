function update_overview(){
	window.planet_set_homeworld.style.display = cdata.home == structure.name || structure.type !== "planet" ? "none" : "initial"
	window.planet_is_homeworld.style.display = cdata.home == structure.name ? "initial" : "none"
	window.planet_set_homeworld.onclick = ()=>{
		send("set-home")
	}
	
	window.in_donate_credits.value = ""
	window.in_donate_credits.placeholder = f.formatNumber(10000)
	window.box_donate_credits.style.display = structure.type === "planet" ? "initial" : "none"
	window.btn_donate_credits.onclick = ()=>{
		var amount = Math.floor(Number(window.in_donate_credits.value))
		var target = structure.name
		send("planet-donate-credits",{amount,target})
	}
}