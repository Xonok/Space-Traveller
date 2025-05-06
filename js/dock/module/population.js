var tick_timer
function update_pop(){
	if(tick_timer){
		clearTimeout(tick_timer)
	}
	var next_tick = f.next_tick("long")
	var seconds = Math.floor(next_tick)
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
	if(!q.structure.industries){return}
	var pop = 0
	q.structure.industries.forEach(i=>{
		var def = q.industry_defs[i.name]
		var el = window.industries
		var tab = "&nbsp;&nbsp;&nbsp;&nbsp;"
		pop += i.workers
		var change = i.growth + i.migration
		var ind_div = f.addElement(el,"div",def.name_display+": ")
		ind_div.style.padding = "2px"
		ind_div.style.marginBottom = "5px"
		// ind_div.style.border = "solid 2px #ff8531"
		ind_div.style.backgroundColor = "#ffca67"
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
		f.tooltip2(ind_div_workers,tt_txt)
		var box = f.addElement(ind_div,"div",tab)
		box.classList.add("horizontal")
		var keys = Object.keys(def.input)
		var img_stack = f.addElement(box,"div")
		img_stack.classList.add("vertical")
		img_stack.style.minWidth = "7rem"
		keys.forEach((k,idx)=>{
			var img_frame = f.addElement(img_stack,"div")
			img_frame.classList.add("horizontal")
			img_frame.style.marginTop = "auto"
			img_frame.style.marginBottom = "auto"
			var img_box = f.img_box(img_frame,"24px","24px",q.idata[k].img)
			img_box.style.marginRight = "2px"
			img_frame.innerHTML += q.idata[k].name
		})
		var arrow_div = f.addElement(box,"div","&nbsp&#10596;&nbsp")
		arrow_div.style.fontSize = "1.5em"
		arrow_div.style.marginTop = "auto"
		arrow_div.style.marginBottom = "auto"
		var img_stack2 = f.addElement(box,"div")
		if(Object.keys(def.output).length){
			var keys2 = Object.keys(def.output)
			keys2.forEach((k,idx)=>{
				var img_frame = f.addElement(img_stack2,"div")
				img_frame.classList.add("horizontal")
				var img_box = f.img_box(img_frame,"24px","24px",q.idata[k].img)
				img_box.style.marginRight = "2px"
				img_frame.innerHTML += q.idata[k].name
			})
		}
		else{
			var img_frame = f.addElement(img_stack2,"div")
			img_frame.classList.add("horizontal")
			img_frame.style.marginTop = "auto"
			img_frame.style.marginBottom = "auto"
			var img_box = f.img_box(img_frame,"24px","24px","img/credits.webp")
			img_box.style.marginRight = "2px"
			img_frame.innerHTML += "Credits"
		}
		ind_div.innerHTML += tab
		var rules = {
			"primary": "Type: Primary",
			"secondary": "Type: Secondary",
			"tertiary": "Type: Tertiary",
			"special": "Type: Special",
			"default": "Type: Unknown"
		}
		ind_div.innerHTML += rules[def.type] || rules[def["default"]]
		ind_div.innerHTML += "<br>"
	})
	window.total_pop.innerHTML = pop ? "<br>Total population: <b>"+pop : "</b>" 
}