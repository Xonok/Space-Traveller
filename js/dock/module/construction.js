
var selected_blueprint
var selected_blueprint_divs=[]
var selected_blueprint_btns=[]
var labor_needed
var category_target
function update_blueprints(){
	if(structure.blueprints){
		var pop = structure.industries.find(ind=>ind.name==="construction")?.workers || 0
		var bots = structure.inventory.items.robots || 0
		var min_pop = Math.max(pop,1000)
		var max_pop = 0
		var max_bots = 0
		structure.inventory.gear.forEach((item,amount)=>{
			var data = idata[item]
			max_pop += data.props?.workers_max_construction*amount || 0
			max_bots += data.props?.robots_max_construction*amount || 0
		})
		var construct = window.construct
		construct.innerHTML = ""
		structure.builds && f.headers(construct,"#","name","progress","status")
		var prev_label
		var time_txt = t=>{
			if(t===Infinity){
				return "never"
			}
			var m = Math.floor(t/8/7/4)
			var w = Math.floor(t/8/7) % 4
			var d = Math.floor(t/8) % 7
			var h = Math.ceil(t)*3 % 24
			var txt = ""
			txt += m ? m+"m" : ""
			txt += w ? w+"w" : ""
			txt += d ? d+"d" : ""
			txt += h ? h+"h" : ""
			return txt
		}
		var total_time_best = 0
		structure.builds?.forEach((b,idx)=>{
			time_left_best = Math.ceil((b.labor_needed-b.labor)/(max_pop+max_bots))
			total_time_best += time_left_best
			var name=idata[b.blueprint].name.replace("Blueprint: ","")
			if(prev_label && prev_label.name === name){
				prev_label.count++
				prev_label.innerHTML = name+" x"+prev_label.count
				prev_label.local_time += time_left_best
				var tt_txt = prev_label.tt_txt
				tt_txt += "<br>This will take: "+time_txt(prev_label.local_time)
				tt_txt += "<br>Done in: "+time_txt(total_time_best)
				f.tooltip2(prev_label,tt_txt)
				return
			}
			var row = f.addElement(construct,"tr")
			var td = f.addElement(row,"td",idx+1) //The 1 is wrong sometimes.
			td.classList.add("centered")
			
			var label = f.addElement(row,"td",name)
			label.name = name
			label.count = 1
			var txt = "Labor: "+f.formatNumber(b.labor)+"/"+f.formatNumber(b.labor_needed)
			txt += "<br><br>(with max pop and bots:)"
			label.tt_txt = txt
			txt += "<br>This will take: "+time_txt(time_left_best)
			txt += "<br>Done in: "+time_txt(total_time_best)
			label.local_time = time_left_best
			f.tooltip2(label,txt)
			var box = f.addElement(row,"td")
			var bar = f.addElement(box,"progress")
			bar.value = b.labor
			labor_needed=b.labor_needed
			bar.max = b.labor_needed
			f.addElement(row,"td",b.active ? "active" : "paused")
			prev_label = label
		})
		var bps = window.blueprints
		bps.innerHTML = ""
		structure.blueprints.forEach(b=>{
			var name=idata[b].name.replace("Blueprint: ","")
			category_target="bp_"+name
			var container=f.addElement(bps,"ul")
			var btn = f.addElement(container,"li",idata[b].name.replace("Blueprint: ",""))
			btn.classList.add("category")
			btn.setAttribute("id",category_target)
			f.tooltip(btn,idata[b.replace("bp_","")])
			btn.onclick = ()=>{
				var info = bp_info[b]
				window.bp_name.innerHTML = idata[b].name.replace("Blueprint: ","")
				var initial = window.inital
				initial.innerHTML = ""
				f.addElement(initial,"label","Initial materials needed:")
				var list = f.addElement(initial,"ul")
				Object.entries(info.inputs).forEach(i=>{
					var item = idata[i[0]]
					var box = f.addElement(list,"li")
					box.classList.add("horizontal")
					var img_box = f.addElement(box,"div")
					img_box.classList.add("centered")
					img_box.style.width = "17px"
					img_box.style.height = "17px"
					img_box.style.marginRight = "5px"
					var img = f.addElement(img_box,"img")
					img.src = item.img
					img.style.maxWidth = "17px"
					img.style.maxHeight = "17px"
					box.innerHTML += i[1]+" "+item.name
				})
				f.addElement(initial,"label","Labor needed: "+f.formatNumber(bp_info[b].labor))
				window.ongoing.innerHTML = ""
				var result = window.result
				result.innerHTML = ""
				f.addElement(result,"label","Result")
				var list3 = f.addElement(result,"ul")
				Object.entries(info.outputs).forEach(i=>{
					var item = idata[i[0]]
					var box = f.addElement(list3,"li")
					box.classList.add("horizontal")
					var img_box = f.addElement(box,"div")
					img_box.classList.add("centered")
					img_box.style.width = "17px"
					img_box.style.height = "17px"
					img_box.style.marginRight = "5px"
					var img = f.addElement(img_box,"img")
					img.src = item.img
					img.style.maxWidth = "17px"
					img.style.maxHeight = "17px"
					box.innerHTML += i[1]+" "+item.name
				})
				window.build.innerHTML = ""
				f.addElement(window.build,"button","Build")
				window.bp_unequip.innerHTML = ""
				f.addElement(window.bp_unequip,"button","Unequip")
				window.build.onclick = ()=>{
					send("start-build",{"blueprint":b})
				}
				window.bp_unequip.onclick = ()=>{
					send("unequip-blueprint",{"blueprint":b})
				}
				selected_blueprint_btns.push(btn)
				selected_blueprint_btns.forEach(d=>{
					d.classList.remove("category_active")
				})
				btn.classList.add("category_active")
			}
			
		})
		var modules_equipped = 0
		structure.inventory.gear.forEach((item,amount)=>{
			var data = idata[item]
			if((data.slot || data.type) === "module"){
				modules_equipped += amount
			}
		})
		var info_panel = window.construction_info_panel
		if(modules_equipped){
			var ind_def = industry_defs["construction"]
			info_panel.innerHTML = ""
			info_panel.innerHTML += "Population: <b>"+pop+"/"+max_pop+"</b>.<br>"
			info_panel.innerHTML += "Robots: <b>"+bots+"/"+max_bots+"<b><br>"
			if(pop === 0){
				info_panel.innerHTML += "No construction can happen yet. <br>Make sure the station has enough food/water/energy and wait until next tick.<br>"
			}
			else if(pop < 1000){
				info_panel.innerHTML += "Population is less than 1000. Construction might take a while.<br>"
			}
			else{info_panel.innerHTML += "<br>"}
			Object.entries(ind_def?.input||{}).forEach(e=>{
				var item = e[0]
				var req = e[1]
				var amount = structure.inventory.items[item] || 0
				var ticks = Math.floor(amount/req/min_pop*1000)
				var hours = (ticks*3%24)+"h"
				var days = Math.floor(ticks*3/24)+"d"
				info_panel.innerHTML += ticks < 1 ? "Not enough <b>"+item + "</b>": "Enough <b>"+item+"</b> for <b>"+days+hours + "</b>"
				info_panel.innerHTML += "<br>"
			})
			info_panel.innerHTML += "^The above numbers don't consider changes in population, but do assume at least 1000 pop."
		}
		else{
			info_panel.innerHTML = "Equip some habitation modules to increase population and use blueprints."
		}
	}
	var i_bps = window.inventory_blueprints
	i_bps.innerHTML = ""
	Object.keys(structure.inventory.items).forEach(i=>{
		var data = idata[i]
		if(data.type==="blueprint"){
			var div = f.addElement(i_bps,"li",data.name.replace("Blueprint: ",""))
			selected_blueprint_divs.push(div)
			div.onclick = ()=>{
				selected_blueprint = i
				selected_blueprint_divs.forEach(d=>{
					d.classList.remove("inventory_blueprints_active")
				})
				div.classList.add("inventory_blueprints_active")
			}
		}
	})
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