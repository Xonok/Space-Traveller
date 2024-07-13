var tick_timer
function update_pop(){
	// why class and not id?
	if(tick_timer){
		clearTimeout(tick_timer)
	}
	var seconds = Math.floor(msg.next_tick)
	tick_timer = setInterval(e=>{
		seconds--
		var minutes = Math.floor(seconds/60)
		var rem_seconds = seconds%60
		if(seconds < 0){
			f.forClass("info_display_tick",e=>{e.innerHTML = "<br>"+"Next tick in: <b>now.</b>"})
			clearTimeout(tick_timer)
		}
		else{
			f.forClass("info_display_tick",e=>{e.innerHTML = "<br>"+"Next tick in: <b>"+String(minutes)+"m"+String(rem_seconds)+"s.</b>"})
		}
		
	},1000)
	
	window.industries.innerHTML = "<span style=\"color:chocolate;font-weight:bold;\">Industries:<br></span>"
	if(!structure.industries){return}
	var pop = 0
	structure.industries.forEach(i=>{
		var def = industry_defs[i.name]
		var el = window.industries
		var tab = "&nbsp;&nbsp;&nbsp;&nbsp;"
		pop += i.workers
		el.innerHTML += def.name_display+" (workers: "
		el.innerHTML += i.workers+", min: "
		el.innerHTML += def.min+", growth: "
		if(i.growth > 0){
			el.innerHTML +="<span style=\"color:green;\">+"+i.growth+"</span>"
		}
		else if(i.growth < 0){
			el.innerHTML +="<span style=\"color:green;\">"+i.growth+"</span>"
		}
		else{
			el.innerHTML +=0
		}
		el.innerHTML +=", migration: "
		if(i.migration > 0){
			el.innerHTML +="<span style=\"color:green;\">+"+i.migration+"</span>"
		}
		else if(i.migration < 0){
			el.innerHTML +="<span style=\"color:red;\">"+i.migration+"</span>"
		}
		else{
			el.innerHTML +=0
		}
		el.innerHTML += ")<br>"
		if(Object.keys(def.input).length){
			el.innerHTML += tab+"Inputs: "
			el.innerHTML += Object.keys(def.input).map(k=>idata[k].name).join(", ")
			el.innerHTML += "<br>"
			if(Object.keys(def.output).length){
				el.innerHTML += tab+"Outputs: "
				el.innerHTML += Object.keys(def.output).map(k=>idata[k].name).join(", ")
				el.innerHTML += "<br>"
			}
			else{
				//el.innerHTML += tab+"Outputs: Credits<br>"
			}
		}
		el.innerHTML += tab
		var rules = {
			"primary": "Type: Primary",
			"secondary": "Type: Secondary",
			"tertiary": "Type: Tertiary",
			"special": "Type: Special",
			"default": "Type: Unknown"
		}
		el.innerHTML += rules[def.type] || rules[def["default"]]
		el.innerHTML += "<br>"
	})
	window.total_pop.innerHTML = pop ? "<br>Total population: <b>"+pop : "</b>" 
}