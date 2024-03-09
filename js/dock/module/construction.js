
var selected_blueprint
var selected_blueprint_divs=[]
function update_blueprints(){
	if(structure.blueprints){
		var construct = window.construct
		construct.innerHTML = ""
		structure.builds && f.headers(construct,"name","progress","status")
		structure.builds?.forEach(b=>{
			var row = f.addElement(construct,"tr")
			f.addElement(row,"td",idata[b.blueprint].name.replace("Blueprint: ",""))
			var box = f.addElement(row,"td")
			var bar = f.addElement(box,"progress")
			bar.value = b.labor
			bar.max = b.labor_needed
			f.addElement(row,"td",b.active ? "active" : "paused")
		})
		// <button>Start</button>
		// <button id="cancel">Cancel</button>
		var bps = window.blueprints
		bps.innerHTML = ""
		structure.blueprints.forEach(b=>{
			var btn = f.addElement(bps,"button",idata[b].name.replace("Blueprint: ",""))
			btn.onclick = ()=>{
				var info = bp_info[b]
				window.bp_name.innerHTML = idata[b].name.replace("Blueprint: ","")
				var initial = window.inital
				initial.innerHTML = ""
				f.addElement(initial,"label","Initial materials needed:")
				var list = f.addElement(initial,"ul")
				Object.entries(info.inputs).forEach(i=>{
					f.addElement(list,"li",i[1]+" "+i[0])
				})
				window.ongoing.innerHTML = ""
				var result = window.result
				result.innerHTML = ""
				f.addElement(result,"label","Result")
				var list3 = f.addElement(result,"ul")
				Object.entries(info.outputs).forEach(i=>{
					f.addElement(list3,"li",i[1]+" "+i[0])
				})
				window.build.innerHTML=""
				f.addElement(window.build,"button","Build")
				window.build.onclick = ()=>{
					send("start-build",{"blueprint":b})
				}
			}
			
		})
		var info_panel = window.construction_info_panel
		var ind_def = industry_defs["construction"]
		var pop = structure.industries.find(ind=>ind.name==="construction").workers || 0
		var min_pop = Math.max(pop,1000)
		info_panel.innerHTML = ""
		if(pop === 0){
			info_panel.innerHTML += "Population is 0. No construction can happen yet. <br>Make sure the station has enough food/water/energy and wait until next tick.<br>"
		}
		else if(pop < 1000){
			info_panel.innerHTML += "Population is less than 1000. Construction might take a while.<br>"
		}
		Object.entries(ind_def.input).forEach(e=>{
			var item = e[0]
			var req = e[1]
			var amount = structure.inventory.items[item] || 0
			var ticks = Math.floor(amount/req/min_pop*1000)
			var hours = (ticks*3%24)+"h"
			var days = Math.floor(ticks*3/24)+"d"
			info_panel.innerHTML += ticks < 1 ? "Not enough "+item : "Enough "+item+" for "+days+hours
			info_panel.innerHTML += "<br>"
		})
		info_panel.innerHTML += "^The above numbers don't consider changes in population, but do assume at least 1000 pop."
	}
	var i_bps = window.inventory_blueprints
	i_bps.innerHTML = ""
	Object.keys(pship.inventory.items).forEach(i=>{
		var data = idata[i]
		if(data.type==="blueprint"){
			var div = f.addElement(i_bps,"div",data.name)
			selected_blueprint_divs.push(div)
			div.onmouseover=()=>{
				div.style.cursor = "pointer"
			}
			div.onclick = ()=>{
				selected_blueprint = i
				selected_blueprint_divs.forEach(d=>{
					d.style.textDecoration="none"
				})
				div.style.textDecoration="underline"
			}
		}
	})
	if(selected_blueprint_divs.length){console.log("blueprints in inventory")}
}

window.equip_blueprint.onclick = do_equip_blueprint
window.construction_admin_next_tick.onclick = do_next_tick
if(!localStorage.getItem("admin")){
	window.construction_admin_next_tick.style.display = "none"
}
function do_equip_blueprint(){
	if(selected_blueprint){
		send("equip-blueprint",{"blueprint":selected_blueprint})
	}
	else{
		f.forClass("error_display",div=>{
			div.innerHTML = div.classList.contains(active_docktab) ? "Click a blueprint name in the list first." : ""
		})
	}
}
function do_next_tick(){
	send("structure-next-tick")
}