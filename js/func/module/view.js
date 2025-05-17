func.view = {
	active: "",
	views: {},
	init(){
		var ready = f=>["complete","interactive"].includes(document.readyState) ? f() : document.addEventListener("DOMContentLoaded",f)

		ready(()=>{
			var view_id = sessionStorage.getItem("view_id") || Object.keys(func.view.views)[0]
			if(func.view.views[view_id]){
				func.view.open(view_id)
			}
		})
	},
	register(name,on_open,on_message){
		var id = "view_"+name
		var el = window[id]
		if(!el){
			throw new Error("View "+name+" requires an element with the id: "+id)
		}
		func.view.views[name] = {
			name,
			el,
			on_open,
			on_message
		}
	},
	open(name){
		if(!func.view.views[name]){
			throw new Error("Unknown view: "+name)
		}
		sessionStorage.setItem("view_id",name)
		if(func.view.active){
			var id = "view_"+func.view.active
			window[id].style.display = "none"
		}
		navbar_update(name)
		func.view.active = name
		func.view.views[name].el.style.display = "initial"
		func.view.views[name].on_open()
	},
	receive(msg){
		var active_view = func.view.views[func.view.active]
		if(!active_view){
			throw new Error("There is no view that is currently active.")
		}
		active_view.on_message(msg)
	}
}