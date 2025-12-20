function update_overview(){
	if(!q.structure){return}
	window.planet_set_homeworld.style.display = q.cdata.home == q.structure.name || q.structure.type !== "planet" ? "none" : "initial"
	window.planet_is_homeworld.style.display = q.cdata.home == q.structure.name ? "initial" : "none"
	window.planet_set_homeworld.onclick = ()=>{
		f.send("set-home")
	}
	
	window.in_donate_credits.value = ""
	window.in_donate_credits.placeholder = f.formatNumber(10000)
	window.box_donate_credits.style.display = q.structure.type === "planet" ? "initial" : "none"
	window.btn_donate_credits.onclick = ()=>{
		var amount = Math.floor(Number(window.in_donate_credits.value))
		var target = q.structure.name
		f.send("planet-donate-credits",{amount,target})
	}
	var rep = 0
	q.structure.props?.rep?.[q.cdata.name]?.forEach((type,amount)=>{
		rep += amount
	})
	var rep_text = "Your reputation: "+Math.floor(rep)+"<br>"
	if(q.structure.type !== "planet"){
		rep_text = ""
	}
	var desc_text = "Owner: "+q.structure.owner+"<br><br>"+rep_text+(q.structure.desc || "No description available")
	f.tooltip2(window.structure_name,desc_text)
	window.planet_desc.innerHTML = f.formatString(desc_text)
}