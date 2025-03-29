var tick_timer
function update_pop(){
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
		var rules = {
			"primary": "Type: Primary",
			"secondary": "Type: Secondary",
			"tertiary": "Type: Tertiary",
			"special": "Type: Special",
			"default": "Type: Unknown"
		}
		pop += i.workers
		console.log(i)
		var change = i.growth + i.migration
		var ind_div = f.addElement(el,"div",def.name_display+": ")
		var ind_div_workers = f.addElement(ind_div,"span",i.workers)
		f.addElement(ind_div,"span"," workers")
		if(change > 0){
			ind_div_workers.style.color = "green"
		}
		if(change < 0){
			ind_div_workers.style.color = "red"
		}
		var style_growth = ""
		if(i.growth){
			style_growth = i.growth > 0 ? "style=color:green" : "style=color:red"
		}
		var style_migration = ""
		if(i.migration){
			style_migration = i.migration > 0 ? "style=color:green" : "style=color:red"
		}
		tt_txt = ""
		tt_txt += "<div>Min: "+def.min+"</div>"
		tt_txt += "Growth: <label "+style_growth+">"+i.growth+"</label>"
		tt_txt += "Migration: <label "+style_migration+">"+i.growth+"</label>"
		tt_txt += rules[def.type] || rules[def["default"]]
		f.tooltip2(ind_div_workers,tt_txt)
		if(Object.keys(def.input).length){
			var box = f.addElement(el,"div")
			box.classList.add("horizontal")
			box.innerHTML = tab+"Inputs: "
			var keys = Object.keys(def.input)
			keys.forEach((k,idx)=>{
				var img_box = f.img_box(box,"17px","17px",idata[k].img)
				img_box.style.marginRight = "2px"
				box.innerHTML += idata[k].name
				if(idx < keys.length-1){
					box.innerHTML += ",&nbsp"
				}
			})
			var box2 = f.addElement(el,"div")
			box2.classList.add("horizontal")
			if(Object.keys(def.output).length){
				box2.innerHTML = tab+"Outputs: "
			}
			var keys2 = Object.keys(def.output)
			keys2.forEach((k,idx)=>{
				var img_box = f.img_box(box2,"17px","17px",idata[k].img)
				img_box.style.marginRight = "2px"
				box2.innerHTML += idata[k].name
				if(idx < keys2.length-1){
					box2.innerHTML += ",&nbsp"
				}
			})
		}
	})
	window.total_pop.innerHTML = pop ? "<br>Total population: <b>"+pop : "</b>" 
}