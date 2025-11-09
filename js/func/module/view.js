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
	register(name,on_open,on_message,on_keydown){
		var id = "view_"+name
		var el = window[id]
		if(!el){
			throw new Error("View "+name+" requires an element with the id: "+id)
		}
		func.view.views[name] = {
			name,
			el,
			on_open,
			on_message,
			on_keydown
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
		chat_update(name)
		var el = func.view.views[name].el
		func.view.active = name
		el.style.display = "initial"
		try{
			func.view.views[name].on_open()
		}
		catch(e){
			f.forClass("error_display",el=>{
				el.innerHTML = e
			})
			console.error(e)
		}
	},
	receive(msg){
		var active_view = func.view.views[func.view.active]
		if(!active_view){
			throw new Error("There is no view that is currently active.")
		}
		try{
			var el = active_view.el
			f.theme.update(el)
			navbar_update(func.view.active)
			chat_update(func.view.active)
			chat_init()
			active_view.on_message(msg)
		}
		catch(e){
			f.forClass("error_display",el=>{
				el.innerHTML = e
			})
			console.error(e)
		}
	},
	view_keydown(e){
		try{
			func.view.views[func.view.active]?.on_keydown?.(e)
		}
		catch(e){
			f.forClass("error_display",el=>{
				el.innerHTML = e
			})
			console.error(e)
		}
		func.keydown_handler(e)
	}
}
window.onkeydown = func.view.view_keydown