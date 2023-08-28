
var selected_blueprint
var selected_blueprint_divs=[]
function update_blueprints(){
	if(structure.blueprints){
		var construct = window.construct
		construct.innerHTML = ""
		structure.builds && f.headers(construct,"name","progress","status")
		structure.builds?.forEach(b=>{
			var row = f.addElement(construct,"tr")
			f.addElement(row,"td",idata[b.blueprint].name.replace(" Blueprint",""))
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
			var btn = f.addElement(bps,"button",idata[b].name.replace(" Blueprint",""))
			btn.onclick = ()=>{
				var info = bp_info[b]
				window.bp_name.innerHTML = idata[b].name.replace(" Blueprint","")
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
function do_equip_blueprint(){
	if(selected_blueprint){
		send("equip-blueprint",{"blueprint":selected_blueprint})
	}
}
