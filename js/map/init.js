var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

function send(command,table={}){
	table.key = key
	table.command = command
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url
				return
			}
			var msg = JSON.parse(e.target.response)
			console.log(msg)
			window.constellation_name.innerHTML = msg.star_data.constellation+": "+star
			update_starmap(msg)
			update_planets(msg)
			map.canvas.update(msg)
			window.info_bar.innerHTML = ""
			Object.entries(msg.star_data.tiles_by_terrain).forEach(e=>{
				var key = e[0]
				var val = e[1]
				window.info_bar.innerHTML += key+": "+val+"<br>"
			})
		}
		else if(e.target.status===400 || e.target.status===500){
			window.error_display.innerHTML = e.target.response
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function update_starmap(msg){
	window.big_map.innerHTML = ""
	var sm = msg.star_data.neighbours
	var make_anchor = (txt)=>{
		if(txt){
			var el = document.createElement("a")
			el.href = "/map.html?star="+txt
			el.innerHTML = txt
			return el
		}
		return ""
	}
	console.log(sm)
	f.row(window.big_map,make_anchor(sm.nw),make_anchor(sm.n),make_anchor(sm.ne))
	f.row(window.big_map,make_anchor(sm.w),make_anchor(star),make_anchor(sm.e))
	f.row(window.big_map,make_anchor(sm.sw),make_anchor(sm.s),make_anchor(sm.se))
}
function update_planets(msg){
	var planets = msg.star_data.planets
	var parent = window.planet_list
	planets.forEach(p=>{
		var title = f.addElement(parent,"div",p.name)
		title.style.marginTop = "10px"
		var box = f.addElement(parent,"div")
		box.classList.add("horizontal")
		var name = f.addElement(box,"div",name)
		var consumes = f.addElement(box,"div","Consumes: ")
		consumes.classList.add("vertical")
		var produces = f.addElement(box,"div","Produces: ")
		Object.values(p.consumes).forEach(c=>{
			var box2 = f.addElement(consumes,"div")
			box2.classList.add("horizontal")
			var img_box = f.addElement(box2,"div")
			img_box.style.width = "25px"
			img_box.style.height = "25px"
			var img = f.addElement(img_box,"img")
			img.src = c.img
			img.style.maxWidth = "25px"
			img.style.maxHeight = "25px"
			img.style.display = "block"
			img.style.margin = "0 auto"
			f.addElement(box2,"div",c.name)
		})
		Object.values(p.produces).forEach(c=>{
			var box2 = f.addElement(produces,"div")
			box2.classList.add("horizontal")
			var img_box = f.addElement(box2,"div")
			img_box.style.width = "25px"
			img_box.style.height = "25px"
			var img = f.addElement(img_box,"img")
			img.src = c.img
			img.style.maxWidth = "25px"
			img.style.maxHeight = "25px"
			img.style.display = "block"
			img.style.margin = "0 auto"
			f.addElement(box2,"div",c.name)
		})
	})
}

var params = new URLSearchParams(window.location.search)
var star = params.get("star")
send("get-map-data",{star})