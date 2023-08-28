function update_pop(){
	// why class and not id?
	f.forClass("info_display",e=>{e.innerHTML = "<br>"+"Next tick in: "+String(Math.floor(msg.next_tick))+" seconds."})
	window.industries.innerHTML = "Industries:<br>"
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
		el.innerHTML += i.growth > 0 ? "+" : ""
		el.innerHTML += (i.growth || 0)+", migration: "
		el.innerHTML += i.migration > 0 ? "+" : ""
		el.innerHTML += (i.migration || 0)+")<br>"
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
	window.total_pop.innerHTML = pop ? "<br>Total population: "+pop : "" 
	window.structure_desc.innerHTML = structure.desc ? f.formatString(structure.desc) + "<br><br>" : ""
}