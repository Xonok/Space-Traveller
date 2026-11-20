var html = {
	init(){
		html.init_categories()
	},
	pagename(){
		return window.location.pathname.split("/").pop().split(".")[0]
	},
	forClass(name,func){
		Array.from(document.getElementsByClassName(name)).forEach(func)
	},
	addElement(parent,type,inner,before=false){
		var e = html.createElement(type,inner)
		before ? parent.prepend(e) : parent.append(e)
		return e
	},
	createElement(type,inner){
		var e = document.createElement(type)
		if(inner!==undefined){e.innerHTML=inner}
		return e
	},
	headers(parent,...names){
		var row = html.addElement(parent,"tr")
		row.type = "headers"
		names.forEach(n=>html.addElement(row,"th",n))
		return row
	},
	row(parent,...data){
		var r = html.addElement(parent,"tr")
		data.forEach(d=>{
			if(typeof d === "number"){
				var el = html.addElement(r,"td",d)
				el.classList.add("align_center")
			}
			else if(typeof d === "string"){
				html.addElement(r,"td",d)
			}
			else if(d.tagName === "TD"){
				r.append(d)
			}
			else if(d instanceof Element){
				html.addElement(r,"td").append(d)
			}
			else{
				console.log(d)
				throw new Error("Unknown element type for row.")
			}
		})
		return r
	},
	add_input(value,func){
		var e = document.createElement("input")
		if(value!== undefined && value !== null){
			e.value = value
			e.saved_value = value
		}
		if(func){e.oninput = func}
		return e
	},
	init_categories(){
		var categories = {}
		html.forClass("btn_category",e=>{
			var cat = e.getAttribute("category_name")
			var tar = e.getAttribute("category_target")
			if(!categories[cat]){
				categories[cat]={
					"buttons": [],
					"targets": []
				}
			}
			categories[cat].buttons.push(e)
			categories[cat].targets.push(tar)
			e.onclick = e2=>{
				categories[cat].targets.forEach(t=>{
					window[t].style.display = "none"
				})
				categories[cat].buttons.forEach(b=>{
					b.classList.remove(cat+"_active")
					b.classList.remove("category_active")
				})
				e.classList.add(cat+"_active")
				e.classList.add("category_active")
				window[tar].style.display = null
				localStorage.setItem(html.pagename()+","+cat+":target",tar)
			}
		})
		html.forClass("category",e=>{
			e.style.display = "none"
		})
		Object.entries(categories).forEach(e=>{
			var name = e[0]
			var data = e[1]
			var target = localStorage.getItem(html.pagename()+","+name+":target")
			data.buttons.forEach((b,idx)=>{
				var tar = b.getAttribute("category_target")
				var do_click = target ? tar===target : !idx
				do_click && b.click()
			})
		})
	}
}
