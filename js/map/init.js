function update_planets(){
	var planets = q.star_data.planets
	var parent = window.planet_list
	parent.innerHTML=""
	planets.forEach(p=>{
		var title = html.addElement(parent,"div",p.name)
		title.style.marginTop = "10px"
		var box = html.addElement(parent,"div")
		box.classList.add("horizontal")
		html.addElement(box,"div",name)
		var consumes = html.addElement(box,"div","Consumes: ")
		consumes.classList.add("vertical")
		var produces = html.addElement(box,"div","Produces: ")
		Object.values(p.consumes).forEach(c=>{
			var box2 = html.addElement(consumes,"div")
			box2.classList.add("horizontal")
			var img_box = html.addElement(box2,"div")
			img_box.style.width = "25px"
			img_box.style.height = "25px"
			var img = html.addElement(img_box,"img")
			img.src = c.img
			img.style.maxWidth = "25px"
			img.style.maxHeight = "25px"
			img.style.display = "block"
			img.style.margin = "0 auto"
			html.addElement(box2,"div",c.name)
		})
		Object.values(p.produces).forEach(c=>{
			var box2 = html.addElement(produces,"div")
			box2.classList.add("horizontal")
			var img_box = html.addElement(box2,"div")
			img_box.style.width = "25px"
			img_box.style.height = "25px"
			var img = html.addElement(img_box,"img")
			img.src = c.img
			img.style.maxWidth = "25px"
			img.style.maxHeight = "25px"
			img.style.display = "block"
			img.style.margin = "0 auto"
			html.addElement(box2,"div",c.name)
		})
	})
}

function map_open(){
	f.send("get-star-data")
}
function map_message(msg){
	window.constellation_name.innerHTML = q.star_data.constellation+": "+q.pship.pos.system
	update_planets()
	map.canvas.update()
	window.info_bar.innerHTML = ""
	Object.entries(q.star_data.tiles_by_terrain).forEach(e=>{
		var key = e[0]
		var val = e[1]
		window.info_bar.innerHTML += key+": "+val+"<br>"
	})
}
f.view.register("map",map_open,map_message)
