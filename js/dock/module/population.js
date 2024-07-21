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
			el.innerHTML +="<span style=\"color:red;\">"+i.growth+"</span>"
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
			var box = f.addElement(el,"div")
			box.classList.add("horizontal")
			box.innerHTML = tab+"Inputs: "
			var keys = Object.keys(def.input)
			keys.forEach((k,idx)=>{
				var img_box = f.addElement(box,"div")
				img_box.classList.add("centered")
				img_box.style.width = "17px"
				img_box.style.height = "17px"
				var img = f.addElement(img_box,"img")
				img.src = idata[k].img
				img.style.maxWidth = "17px"
				img.style.maxHeight = "17px"
				box.innerHTML += idata[k].name
				if(idx > keys.length){
					box.innerHTML += ", "
				}
			})
			var box2 = f.addElement(el,"div")
			box2.classList.add("horizontal")
			if(Object.keys(def.output).length){
				box2.innerHTML = tab+"Outputs: "
			}
			var keys2 = Object.keys(def.output)
			keys2.forEach((k,idx)=>{
				var img_box = f.addElement(box2,"div")
				img_box.classList.add("centered")
				img_box.style.width = "17px"
				img_box.style.height = "17px"
				var img = f.addElement(img_box,"img")
				img.src = idata[k].img
				img.style.maxWidth = "17px"
				img.style.maxHeight = "17px"
				box2.innerHTML += idata[k].name
				if(idx > keys.length){
					box2.innerHTML += ", "
				}
			})
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